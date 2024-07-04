from django.utils.dateformat import format

from .models import Message
from rest_framework.serializers import ModelSerializer, SerializerMethodField


class MessageSerializer(ModelSerializer):
    sender = SerializerMethodField()
    created = SerializerMethodField()
    time = SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            "id",
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
