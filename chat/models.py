from django.db.models import FileField, TextChoices
from django.conf import settings

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


class Chat(Model):
    id = UUIDField(primary_key=True, editable=False, default=uuid4)
    artist = ForeignKey(Artist, related_name="chat_artists", on_delete=CASCADE)
    collector = ForeignKey(Collector, related_name="chat_collectors", on_delete=CASCADE)
    is_artist_online = BooleanField(default=False, db_index=True)
    is_collector_online = BooleanField(default=False, db_index=True)
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
    message_type = CharField(max_length=3, choices=MessageType.choices, default=MessageType.TEXT, db_index=True)
    content = TextField(blank=True, db_index=True)
    audio_content = FileField(upload_to="audio/", blank=True, db_index=True)
    is_reply = BooleanField(default=False, db_index=True)
    previous_sender = CharField(max_length=50, blank=True, null=True, db_index=True)  # Username of the replied message's sender
    previous_content = TextField(blank=True, null=True, db_index=True)  # Content of the replied message
    previous_message_id = UUIDField(blank=True, null=True, db_index=True)  # Id of the replied message
    sender = ForeignKey(User, related_name="sent_messages", on_delete=CASCADE)
    chat = ForeignKey(Chat, related_name="chat_messages", on_delete=CASCADE)
    created = DateTimeField(auto_now_add=True, db_index=True)
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
                api_key=settings.CLOUDINARY_STORAGE["API_KEY"],
                api_secret=settings.CLOUDINARY_STORAGE["API_SECRET"],
                cloud_name=settings.CLOUDINARY_STORAGE["CLOUD_NAME"],
            )
        return super().delete(*args, **kwargs)
