from django.contrib.admin import ModelAdmin, register

from .models import User, Artist, Collector, JWTTokenBlacklist


@register(User)
class UserAdmin(ModelAdmin):
    list_display = ["id", "email", "username", "password", "is_active",
                    "is_superuser", "is_staff", "created", "updated", "last_login"]
    list_filter = ["id", "email", "username", "is_superuser", "created", "last_login"]
    
    
@register(Artist)
class ArtistAdmin(ModelAdmin):
    list_display = ["id", "bio", "instagram", "user", "created", "updated"]
    list_filter = ["id", "instagram", "user", "created"]
    
    
@register(Collector)
class CollectorAdmin(ModelAdmin):
    list_display = ["id", "bio", "instagram", "user", "created", "updated"]
    list_filter = ["id", "instagram", "user", "created"]
    
    
@register(JWTTokenBlacklist)
class JWTTokenBlacklistAdmin(ModelAdmin):
    list_display = ["token", "user"]
    list_filter = ["user"]
    verbose_name = "Blacklisted Token"
    verbose_name_plural = "Blacklisted Tokens"