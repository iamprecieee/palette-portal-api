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
    id = UUIDField(primary_key=True, editable=False, default=uuid4)
    content = TextField(blank=False)
    is_reply = BooleanField(default=False)
    previous_sender = CharField(max_length=50, blank=True, null=True)
    previous_content = TextField(blank=True, null=True)
    previous_message_id = UUIDField(blank=True, null=True)
    sender = ForeignKey(User, related_name="sent_messages", on_delete=CASCADE)
    chat = ForeignKey(Chat, related_name="chat_messages", on_delete=CASCADE)
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"Message from {self.sender}"