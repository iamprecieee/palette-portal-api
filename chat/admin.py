from django.contrib.admin import register, ModelAdmin

from .models import Chat, Message


@register(Chat)
class ChatAdmin(ModelAdmin):
    list_display = ["id", "artist", "collector", "created"]
    list_filter = ["id", "created"]


@register(Message)
class MessageAdmin(ModelAdmin):
    list_display = [
        "id",
        "content",
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
