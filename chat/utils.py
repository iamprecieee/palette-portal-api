from django.conf import settings
from django.utils.dateformat import format

from user.views import User
from .views import Chat, Message, MessageSerializer

from channels.db import database_sync_to_async
import jwt
from uuid import UUID


@database_sync_to_async
def confirm_authorization(headers):
    """
    Checks for auth token in headers and uses it to retrieve current `request.user` object.
    Note: This supports only simple_jwt at the moment.
    """
    if b"authorization" in headers and b"Bearer" in headers[b"authorization"]:
        token = headers[b"authorization"].decode().split(" ")[1]
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload["user_id"]

        return User.objects.filter(id=user_id).first()


@database_sync_to_async
def get_chat_members(chat_id):
    chat = Chat.objects.filter(id=chat_id).first()
    if chat:
        return (chat.artist.user, chat.collector.user)


@database_sync_to_async
def create_new_message(user, content, chat_id):
    new_message = Message.objects.create(sender=user, content=content, chat_id=chat_id)
    return new_message.id, new_message.created


@database_sync_to_async
def get_replied_message(message_id, chat_id):
    message = Message.objects.filter(id=message_id, chat_id=chat_id).first()
    return MessageSerializer(message).data


@database_sync_to_async
def create_new_reply(
    user, content, previous_sender, previous_content, message_id, chat_id
):
    message_id = UUID(message_id)
    new_reply = Message.objects.create(
        sender=user,
        content=content,
        previous_sender=previous_sender,
        previous_content=previous_content,
        previous_message_id=message_id,
        chat_id=chat_id,
        is_reply=True,
    )
    return new_reply.id, new_reply.created


@database_sync_to_async
def set_user_status(user, chat_id, status):
    chat = Chat.objects.filter(id=chat_id).first()
    if chat:
        if status == "online":
            if user == chat.artist.user:
                chat.is_artist_online = True
            else:
                chat.is_collector_online = True
        else:
            if user == chat.artist.user:
                chat.is_artist_online = False
            else:
                chat.is_collector_online = False
        chat.save()
