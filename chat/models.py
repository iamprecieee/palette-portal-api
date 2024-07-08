from django.db.models import FileField, TextChoices, PositiveIntegerField
from django.core.files.storage import FileSystemStorage

from user.models import (
    Model,
    UUIDField,
    uuid4,
    ForeignKey,
    Artist,
    Collector,
    CASCADE,
    DateTimeField,
    User,
    TextField,
    BooleanField,
    CharField,
)

from cloudinary.uploader import destroy
import os


class Chat(Model):
    id = UUIDField(primary_key=True, editable=False, default=uuid4)
    artist = ForeignKey(Artist, related_name="chat_artists", on_delete=CASCADE)
    collector = ForeignKey(Collector, related_name="chat_collectors", on_delete=CASCADE)
    is_artist_online = BooleanField(default=False)
    is_collector_online = BooleanField(default=False)
    created = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"Chat between {self.artist.user.username} and {self.collector.user.username}"


class Message(Model):
    class MessageType(TextChoices):
        TEXT = "TXT", "Text"
        AUDIO = "AUD", "Audio"

    id = UUIDField(primary_key=True, editable=False, default=uuid4)
    message_type = CharField(
        max_length=3, choices=MessageType.choices, default=MessageType.TEXT
    )
    content = TextField(blank=True)
    audio_content = FileField(upload_to="audio/", blank=True)
    is_reply = BooleanField(default=False)
    previous_sender = CharField(
        max_length=50, blank=True, null=True
    )  # Username of the replied message's sender
    previous_content = TextField(
        blank=True, null=True
    )  # Content of the replied message
    previous_message_id = UUIDField(blank=True, null=True)  # Id of the replied message
    sender = ForeignKey(User, related_name="sent_messages", on_delete=CASCADE)
    chat = ForeignKey(Chat, related_name="chat_messages", on_delete=CASCADE)
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"{self.get_message_type_display()} message from {self.sender}"

    # Extending the `delete` method to also remove the deleted audio from cloudinary
    def delete(self, *args, **kwargs):
        if self.audio_content:
            public_id = self.audio_content.name
            destroy(
                public_id=public_id,
                api_key=os.getenv("API_KEY"),
                api_secret=os.getenv("API_SECRET"),
                cloud_name=os.getenv("CLOUD_NAME"),
            )
        return super().delete(*args, **kwargs)
