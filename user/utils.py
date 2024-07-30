from uuid import uuid4
from pyotp import TOTP, random_base32


def generate_default_username():
    return f"user{str(uuid4())}"


def generate_otp_code(email, otp_type=None):
    from .models import User, UserOTP # To avoid circular imports

    user = User.objects.filter(email=email).first()
    if user:
        otp_code =  TOTP(random_base32(), digits=6).now()
        if otp_type:
            UserOTP.objects.create(otp_code=otp_code, user=user, otp_type=UserOTP.OTPType.PASSWORD)
        else:
            UserOTP.objects.create(otp_code=otp_code, user=user)
            
        return otp_code, str(user.id)