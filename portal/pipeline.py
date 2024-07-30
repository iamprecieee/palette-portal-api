from social_core.pipeline.user import USER_FIELDS
from user.tasks import send_otp


def custom_create_user(backend, details, user=None, *args, **kwargs):
    """ 
    Checks if user exists with a verified email, or creates a new user and sends a verification email.
    """
    if user:
        if not user.is_email_verified:
            raise ValueError("Existing user's email has not been verified. Check your email for a verification link or request a new one.")
        else:
            return {"is_new": False}
        
    fields = {
        name: kwargs.get(name, details.get(name))
        for name in backend.setting("USER_FIELDS", USER_FIELDS)
    }
    if not fields:
        return
    
    fields["password"] = "social"
    fields["is_email_verified"] = True
    user = backend.strategy.create_user(**fields)
    send_otp.delay(user.email)
    return {"is_new": True, "user": user}