from django.db.transaction import atomic, on_commit
from django.db import IntegrityError
from django.utils import timezone
from django.core import signing

from .models import User, Artist, Collector, PaletteAuthToken, UserOTP
from .refresh import SessionRefreshToken
from .tasks import store_access_token, send_otp

from rest_framework.serializers import (
    ModelSerializer,
    CharField,
    ValidationError,
    EmailField,
    Serializer,
    SerializerMethodField,
)
from rest_framework.authentication import authenticate
from rest_framework.exceptions import AuthenticationFailed
import re
from rest_framework_simplejwt.tokens import RefreshToken


class RegisterSerializer(ModelSerializer):
    password = CharField(write_only=True)
    confirm_password = CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "username", "password", "confirm_password"]
        read_only_fields = ["id", "username"]

    def validate(self, data):
        password = data["password"]
        confirm_password = data["confirm_password"]

        if len(password) < 8:
            raise ValidationError(
                {"password": "Password must contain at least 8 characters."}
            )
            
        if not re.search(r"[0-9]", password):
            raise ValidationError(
                {"password": "Password must contain at least 1 number."}
            )

        if not re.search(r"[A-Z]", password):
            raise ValidationError(
                {"password": "Password must contain at least 1 uppercase letter."}
            )

        if not re.search(r'[!@#$%^&*()_+=,.?/\|":;`~]', password):
            raise ValidationError(
                {"password": "Password must contain at least 1 symbol."}
            )

        if password != confirm_password:
            raise ValidationError({"password": "Passwords do not match."})

        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        return User.objects.create_user(**validated_data)
    
    
class RequestEmailVerificationSerializer(Serializer):
    email = CharField()
    
    def validate(self, data):
        email = data.get("email")
        if not email:
            raise ValidationError({"email": "Email field is required."})
        
        self.user = User.objects.filter(email=email).first()
        if not self.user:
            raise ValidationError({"email": "This email does not belong to an existing user."})
        
        if UserOTP.objects.filter(user=self.user, otp_type=UserOTP.OTPType.EMAIL).exists():
            raise ValidationError({"OTP": "Please check your email for an existing verification link."})
        
        return data
    
    def save(self, **kwargs):
        send_otp.delay(self.user.email)
        
    
class EmailVerificationOTPSerializer(Serializer):
    token = CharField(write_only=True)
    
    def validate(self, data):
        try:
            (otp_code, user_id) = signing.loads(data["token"])
        except signing.BadSignature:
            raise ValidationError({"OTP": "Invalid OTP code detected."})
        
        self.otp = UserOTP.objects.filter(otp_code=otp_code, user_id=user_id).first()
        if not self.otp:
            raise ValidationError({"OTP": "OTP code has been used or never existed."})
        
        self.otp_user = self.otp.user
        if self.otp_user.is_email_verified:
            self.otp.delete()
            raise ValidationError({"OTP": "This user's email has already been verified."})
        
        elif timezone.now() > self.otp.expiry:
            self.otp.delete()
            on_commit(lambda: send_otp.delay(self.otp_user.email))
            raise ValidationError({"OTP": "OTP code is invalid. A new code has been sent to your email."})
        
        return data
                
    
    def save(self, **kwargs):
        self.otp_user.is_email_verified = True
        self.otp_user.save()
        self.otp.delete()
        
        
class PasswordChangeSerializer(Serializer):
    email = CharField()
    
    def validate(self, data):
        email = data.get("email")
        if not email:
            raise ValidationError({"email": "Email field is required."})
        
        self.user = User.objects.filter(email=email).first()
        if not self.user:
            raise ValidationError({"email": "This email does not belong to an existing user."})
        
        if UserOTP.objects.filter(user=self.user, otp_type=UserOTP.OTPType.PASSWORD).exists():
            raise ValidationError({"OTP": "Please check your email for an existing password change link."})
        
        return data
    
    def save(self, **kwargs):
        send_otp.delay(self.user.email, otp_type="password")
        
        
class PasswordChangeSerializer(Serializer):
    password = CharField(write_only=True)
    confirm_password = CharField(write_only=True)
    
    def validate(self, data):
        self.password = data.get("password")
        confirm_password = data.get("confirm_password")
        if not self.password:
            raise ValidationError({"password": "Password field is required."})
        elif not confirm_password:
            raise ValidationError({"password": "Confirm Password field is also required."})
        
        token = self.context["token"]
        try:
            (otp_code, user_id) = signing.loads(token)
        except signing.BadSignature:
            raise ValidationError({"OTP": "Invalid OTP code detected."})
        
        self.otp = UserOTP.objects.filter(otp_code=otp_code, user_id=user_id).first()
        self.otp_user = self.otp.user
        if not self.otp:
            raise ValidationError({"OTP": "OTP code has been used or never existed."})
        
        elif timezone.now() > self.otp.expiry:
            self.otp.delete()
            on_commit(lambda: send_otp.delay(self.otp_user.email, otp_type="password"))
            raise ValidationError({"OTP": "OTP code is invalid. A new code has been sent to your email."})
        
        if len(self.password) < 8:
            raise ValidationError(
                {"password": "Password must contain at least 8 characters."}
            )
            
        if not re.search(r"[0-9]", self.password):
            raise ValidationError(
                {"password": "Password must contain at least 1 number."}
            )

        if not re.search(r"[A-Z]", self.password):
            raise ValidationError(
                {"password": "Password must contain at least 1 uppercase letter."}
            )

        if not re.search(r'[!@#$%^&*()_+=,.?/\|":;`~]', self.password):
            raise ValidationError(
                {"password": "Password must contain at least 1 symbol."}
            )

        if self.password != confirm_password:
            raise ValidationError({"password": "Passwords do not match."})
        
        return data
    
    def save(self, **kwargs):
        with atomic():
            self.otp_user.set_password(self.password)
            self.otp_user.is_social_password_updated = True
            self.otp_user.save()
            self.otp.delete()


class KnoxLoginSerializer(ModelSerializer):
    """
    Serializer for knox-based login.
    Updates `last_login` and deletes extra auth tokens.
    """
    email = EmailField()
    password = CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "username", "password"]
        read_only_fields = ["id", "username"]

    def authenticate_user(self):
        request = self.context["request"]
        email = request.data["email"]
        password = request.data["password"]
        user = authenticate(request, email=email, password=password)
        if not user:
            raise AuthenticationFailed(
                "No active account found with the given credentials."
            )

        user.save(update_fields=["last_login"])
        with atomic():
            from .tasks import delete_extra_palette_token
            _, token = PaletteAuthToken.objects.create(user)
            delete_extra_palette_token.delay(user.id)
                
        return user, token


class RefreshTokenSerializer(Serializer):
    """
    Serializer for generating new access tokens, and blacklisting refresh tokens.
    Previous refresh token is blacklisted and replaced by a new token.
    """

    token_class = RefreshToken
    access = CharField(read_only=True)
    refresh = CharField(read_only=True)

    def validate(self):
        context = self.context
        session_refresh = SessionRefreshToken(context["request"])
        refresh = self.token_class(context["refresh"])
        access_data = {"access": str(refresh.access_token)}
        access_data["refresh"] = str(refresh)

        session_refresh.remove()
        session_refresh.add(access_data["refresh"])
        store_access_token.delay(access_data["access"])

        return access_data


class ArtistProfileSerializer(ModelSerializer):
    user = SerializerMethodField()

    class Meta:
        model = Artist
        fields = ["id", "bio", "instagram", "user"]
        read_only_fields = ["id"]

    def get_user(self, obj):
        return str(obj.user)

    def create(self, validated_data):
        user = self.context["user"]
        validated_data["user"] = user
        try:
            with atomic():
                profile = Artist.objects.create(**validated_data)
        except IntegrityError:
            raise IntegrityError("This user has an existing artist profile.")

        return profile

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class CollectorProfileSerializer(ModelSerializer):
    user = SerializerMethodField()

    class Meta:
        model = Collector
        fields = ["id", "bio", "instagram", "user"]
        read_only_fields = ["id"]

    def get_user(self, obj):
        return str(obj.user)

    def create(self, validated_data):
        user = self.context["user"]
        validated_data["user"] = user
        try:
            with atomic():
                profile = Collector.objects.create(**validated_data)
        except IntegrityError:
            raise IntegrityError("This user has an existing collector profile.")

        return profile

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
