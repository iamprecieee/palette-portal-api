from django.utils.dateformat import format

from .models import Message, Chat
from rest_framework.serializers import ModelSerializer, SerializerMethodField


class MessageSerializer(ModelSerializer):
    sender = SerializerMethodField()
    created = SerializerMethodField()
    time = SerializerMethodField()
    content = SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            "id",
            "message_type",
            "content",
            "is_reply",
            "previous_sender",
            "previous_content",
            "previous_message_id",
            "sender",
            "created",
            "time",
        ]

    def get_sender(self, obj):
        return obj.sender.username

    def get_created(self, obj):
        return format(obj.created, "M. d, Y")

    def get_time(self, obj):
        return format(obj.created, "P")
    
    def get_content(self, obj):
        return obj.audio_content if obj.get_message_type_display() == "Audio" else obj.content


class ChatSerializer(ModelSerializer):
    class Meta:
        model = Chat
        fields = [
            "id",
            "artist",
            "collector",
            "created",
        ]
        read_only_fields = ["id", "created"]
        