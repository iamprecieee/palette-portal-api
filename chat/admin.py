from django.contrib.admin import register, ModelAdmin

from .models import Chat, Message


@register(Chat)
class ChatAdmin(ModelAdmin):
    list_display = ["id", "artist", "collector", "is_artist_online", "is_collector_online", "created"]
    list_filter = ["id", "created"]


@register(Message)
class MessageAdmin(ModelAdmin):
    list_display = [
        "id",
        "message_type",
        "content",
        "audio_content",
        "is_reply",
        "previous_sender",
        "previous_content",
        "previous_message_id",
        "sender",
        "chat",
        "created",
        "updated",
    ]
    list_filter = ["id", "sender", "created", "updated"]
    