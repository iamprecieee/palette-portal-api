from django.conf import settings
from django.utils.dateformat import format
from django.db.transaction import atomic

from user.views import User
from .views import Chat, Message, MessageSerializer

from channels.db import database_sync_to_async
import jwt
from time import time
from random import randint
from base64 import b64encode, b64decode
import os
from cloudinary.uploader import upload
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
    """ 
    Retrieves the artist and collector for a particular chat if it exists.
    """
    chat = Chat.objects.select_related("artist__user", "collector__user").filter(id=chat_id).first()
    if chat:
        return (chat.artist.user, chat.collector.user)


@database_sync_to_async
def set_user_status(user, chat_id, status):
    """ 
    Updates `online` status of a chat member in the database.
    """
    chat = Chat.objects.select_related("artist__user", "collector__user").filter(id=chat_id).first()
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


@database_sync_to_async
def generate_random_filename():
    timestamp = int(time() * 1000)  # Get the current timestamp in milliseconds
    random_num = randint(0, 999999)  # Generate a random number between 0 and 999999
    return f"recording_{timestamp}_{random_num}.wav"


@database_sync_to_async
def create_new_audio_message(user, chat_id):
    new_audio_message = Message.objects.create(
        sender=user, chat_id=chat_id, message_type=Message.MessageType.AUDIO
    )
    return new_audio_message.id, new_audio_message.created


@database_sync_to_async
def update_audio_message(audio_id, content, filename):
    """
    Saves the decoded audio data to temporary storage, and uploads from there to cloudinary.
    The audio object is then updated with the cloud details and temporary file is removed at the end.
    """
    audio_data = b64decode(content)
    temp_file_path = os.path.join(settings.MEDIA_ROOT, "temp_uploads", filename)

    # Ensure the directory exists
    os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)
    with open(temp_file_path, "wb") as file:
        file.write(audio_data)

    response = upload(
        temp_file_path,
        resource_type="auto",
        api_key=os.getenv("API_KEY"),
        api_secret=os.getenv("API_SECRET"),
        cloud_name=os.getenv("CLOUD_NAME"),
    )
    final_url = response["secure_url"]
    audio_message = Message.objects.filter(id=audio_id).first()
    with atomic():
        audio_message.audio_content = final_url
        audio_message.save()

    os.remove(temp_file_path)


@database_sync_to_async
def get_replied_message(message_id, chat_id):
    """ 
    Retrieves the message that was replied to.
    """
    message = Message.objects.filter(id=message_id, chat_id=chat_id).first()
    return MessageSerializer(message).data


@database_sync_to_async
def create_new_reply(user, content, previous_sender, previous_content, message_id, chat_id):
    """ 
    Create a new 'reply' message.
    """
    message_id = UUID(message_id)
    if content == "audio":
        new_reply = Message.objects.create(
            sender=user,
            previous_sender=previous_sender,
            previous_content=previous_content,
            previous_message_id=message_id,
            chat_id=chat_id,
            is_reply=True,
            message_type=Message.MessageType.AUDIO,
        )
    else:
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
def create_new_message(user, content, chat_id):
    """ 
    Create a new 'non-reply' message.
    """
    new_message = Message.objects.create(sender=user, content=content, chat_id=chat_id)
    return new_message.id, new_message.created
