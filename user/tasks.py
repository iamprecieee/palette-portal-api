from django.db.transaction import atomic
from django.utils import timezone
from django.core.cache import cache
from django.core.mail import send_mail
from django.core import signing
from django.conf import settings

from .models import PaletteAuthToken, JWTAccessToken, Artist, User, Collector
from .utils import generate_otp_code

from celery import shared_task
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework_simplejwt.tokens import AccessToken
import pickle


@shared_task
def delete_extra_palette_token(user_id):
    palette_auth_token = PaletteAuthToken.objects.filter(user_id=user_id)
    while palette_auth_token.count() > 3:
        palette_auth_token.last().delete()
        
        
@shared_task
def store_access_token(access_token):
    decoded_token = AccessToken(access_token)
    user_id = decoded_token["user_id"]
    token = JWTAccessToken.objects.filter(user_id=user_id)
    with atomic():
        if token.count() > 0:
            token.last().delete()
        
        user = User.objects.filter(id=user_id).first()
        JWTAccessToken.objects.create(token=access_token, user=user)
        
        
@shared_task
def delete_access_token(user_id):
    JWTAccessToken.objects.filter(user_id=user_id).delete()
        
        
@shared_task
def cleanup_expired_refresh_tokens():
    now = timezone.now()
    expired_tokens = OutstandingToken.objects.filter(expires_at__lt=now)
    expired_tokens.delete()
    
    
@shared_task
def update_cache_details(object_id, profile_id, is_delete=False, is_collector=False):
    object_model = Collector if is_collector else Artist
    object_prefix = "collector" if is_collector else "artist" 
    profile = object_model.objects.filter(id=object_id).first()
    profiles_cache = pickle.loads(cache.get(f"{object_prefix}_list", []))
    profiles_cache_ids = [i.id for i in profiles_cache if str(i.id) != str(profile_id)]
    if not is_delete:
        profiles_cache_ids.append(profile.id)
        
    object_list = object_model.objects.filter(id__in=profiles_cache_ids)
    cache.set(f"{object_prefix}_list", pickle.dumps(object_list))
       
       
       
@shared_task
def send_otp(email, otp_type=None):
    otp_code, user_id = generate_otp_code(email, otp_type)
    signed_token = signing.dumps((otp_code, user_id))
    current_host = settings.CURRENT_HOST
    sender_email = settings.SENDER_EMAIL
    if otp_type:
        verification_url = f"https://{current_host}/api/v1/user/change-password/complete/{signed_token}/"
        html_message=f"""
            <html>
                <body>
                    <p>
                        Click this link to change your password:<br>
                        <a href="{verification_url}">verification link</a>
                    </p>
                </body>
            </html>
        """
        subject = "Password Change"
    else:
        verification_url = f"https://{current_host}/api/v1/user/verify-email/complete/{signed_token}/"
        html_message=f"""
            <html>
                <body>
                    <p>
                        Click this link to verify your email:<br>
                        <a href="{verification_url}">verification link</a>
                    </p>
                </body>
            </html>
        """
        subject = "Email Verification"
    
    send_mail(
        subject=subject,
        message=html_message,
        from_email=sender_email,
        recipient_list=[email],
        html_message=html_message,
        fail_silently=False
    )
  