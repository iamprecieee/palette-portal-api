from django.contrib.admin import ModelAdmin, register

from .models import (
    User, 
    Artist, 
    Collector, 
    JWTAccessToken, 
    PaletteAuthToken, 
    UserOTP
)


@register(User)
class UserAdmin(ModelAdmin):
    list_display = [
        "id",
        "email",
        "username",
        "password",
        "is_active",
        "is_superuser",
        "is_staff",
        "created",
        "updated",
        "last_login",
    ]
    list_filter = ["id", "email", "username", "is_superuser", "created", "last_login"]


@register(Artist)
class ArtistAdmin(ModelAdmin):
    list_display = ["id", "bio", "instagram", "user", "created", "updated"]
    list_filter = ["id", "instagram", "user", "created"]


@register(Collector)
class CollectorAdmin(ModelAdmin):
    list_display = ["id", "bio", "instagram", "user", "created", "updated"]
    list_filter = ["id", "instagram", "user", "created"]


@register(JWTAccessToken)
class JWTAccessTokenAdmin(ModelAdmin):
    list_display = ["token", "user"]
    list_filter = ["user"]
    verbose_name = "JWT Access Token"
    verbose_name_plural = "JWT Access Tokens"
    
    
@register(PaletteAuthToken)
class PaletteAuthTokenAdmin(ModelAdmin):
    list_display = ["digest", "token_key", "user", "created", "expiry"]
    list_filter = ["digest", "user"]
    verbose_name = "Palette Auth Token"
    verbose_name_plural = "Palette Auth Tokens"
    
    
@register(UserOTP)
class UserOTPAdmin(ModelAdmin):
    list_display = ["otp_code", "otp_type", "expiry", "user"]
    list_filter = ["otp_code", "otp_type", "expiry", "user"]
