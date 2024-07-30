from .utils import *

import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Initiates handshake to connect our consumer to the websocket client and join the chat group.
        This includes an extra authorization check for the `request.user` to ensure user is part of the current chat.
        """
        # Retrieve the `chat_id` value from scope and use it to set group room name
        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        self.chat_group_name = f"chat_{self.chat_id}"

        headers = dict(self.scope["headers"])  # Headers dict should contain the authentication token
        user = await confirm_authorization(headers)
        self.user = user
        self.username = user.username
        chat = await get_chat_members(self.chat_id)  # Retrieves the users in the current chat
        if not user in chat:
            await self.close(code=4001)

        # Join chat group
        await self.channel_layer.group_add(self.chat_group_name, self.channel_name)

        # Confirm connection to websocket
        await self.accept()

        # Send message for online status and update db
        await self.channel_layer.group_send(
            self.chat_group_name,
            {"type": "chat.status", "content": "online", "username": self.username},
        )
        await set_user_status(self.user, self.chat_id, status="online")

    async def disconnect(self, close_code):
        """
        Sends message for offline status, leaves chat group, and updates db accordingly.
        """
        await self.channel_layer.group_send(
            self.chat_group_name,
            {
                "type": "chat.status",
                "content": "offline",
                "username": self.username,
            },
        )
        await self.channel_layer.group_discard(self.chat_group_name, self.channel_name)
        await set_user_status(self.user, self.chat_id, status="offline")

    # Receive message from websocket client
    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data:
            """
            Seperates the bytes data into its audio and json components using the delimiter(plain text).
            Audio data is base64-encoded, while Json data is decoded and loaded into a metadata variable.
            The message is then processed and sent as normal audio, or as an audio reply.
            """
            # Define the delimiter
            delimiter = b"<delimiter>"

            # Separate the JSON metadata from the audio data using the delimiter
            if delimiter in bytes_data:
                json_data, audio_data = bytes_data.split(delimiter, 1)

                # Decode the JSON metadata
                metadata = json.loads(json_data.decode("utf-8"))
                message_type = metadata.get("type")

                # Handle binary data (audio message)
                filename = await generate_random_filename()
                message = b64encode(audio_data).decode("utf-8")  # Encode to base64 for sending as text

                if message_type == "audio":
                    """ 
                    For 'non-reply' audio messages.
                    """
                    audio_message_id, created = await create_new_audio_message(
                        self.user, self.chat_id
                    )

                    await self.channel_layer.group_send(
                        self.chat_group_name,
                        {
                            "type": "chat.audio",
                            "content": message,
                            "filename": filename,
                            "time": format(created, "P"),
                            "sender": self.username,
                            "id": str(audio_message_id),
                        },
                    )
                    await update_audio_message(audio_message_id, message, filename)
                else:
                    """ 
                    For 'reply' audio messages.
                    """
                    previous_message_id = metadata.get("previous_message_id")
                    replied_message = await get_replied_message(
                        previous_message_id, self.chat_id
                    )
                    if replied_message["message_type"] == "AUD":
                        previous_content = "AUDIO"
                    else:
                        previous_content = replied_message["content"]

                    content = "audio"
                    reply_id, created = await create_new_reply(
                        self.user,
                        content,
                        replied_message["sender"],
                        previous_content,
                        previous_message_id,
                        self.chat_id,
                    )
                    await self.channel_layer.group_send(
                        self.chat_group_name,
                        {
                            "type": "chat.reply",
                            "reply_format": "audio",
                            "content": message,
                            "previous_sender": replied_message["sender"],
                            "previous_content": previous_content,
                            "previous_message_id": previous_message_id,
                            "time": format(created, "P"),
                            "sender": self.username,
                            "id": str(reply_id),
                        },
                    )
                    await update_audio_message(reply_id, message, filename)
        else:
            text_data_json = json.loads(text_data)
            message = text_data_json.get("message")
            message_type = text_data_json.get("type")

            # Send message to chat group
            if message_type == "typing":
                """ 
                For 'typing' status messages.
                """
                await self.channel_layer.group_send(
                    self.chat_group_name,
                    {
                        "type": "chat.typing",
                        "username": self.username,
                        "content": (
                            f"{self.user} is typing..."
                            if message == "typing"
                            else str(self.user)
                        ),
                    },
                )
            elif message_type == "message":
                """ 
                For 'non-reply' text messages.
                """
                if message:
                    message_id, created = await create_new_message(
                        self.user, message, self.chat_id
                    )

                    await self.channel_layer.group_send(
                        self.chat_group_name,
                        {
                            "type": "chat.message",
                            "content": message,
                            "created": format(created, "M. d, Y"),
                            "time": format(created, "P"),
                            "sender": self.username,
                            "id": str(message_id),
                        },
                    )
            elif message_type == "reply":
                """ 
                For 'reply' text messages.
                """
                previous_message_id = text_data_json.get("previous_message_id")
                if message:
                    replied_message = await get_replied_message(
                        previous_message_id, self.chat_id
                    )
                    if replied_message["message_type"] == "AUD":
                        previous_content = "AUDIO"
                    else:
                        previous_content = replied_message["content"]

                    reply_id, created = await create_new_reply(
                        self.user,
                        message,
                        replied_message["sender"],
                        previous_content,
                        previous_message_id,
                        self.chat_id,
                    )
                    await self.channel_layer.group_send(
                        self.chat_group_name,
                        {
                            "type": "chat.reply",
                            "reply_format": "text",
                            "content": message,
                            "previous_sender": replied_message["sender"],
                            "previous_content": previous_content,
                            "previous_message_id": previous_message_id,
                            "time": format(created, "P"),
                            "sender": self.username,
                            "id": str(reply_id),
                        },
                    )

    # Receive message from room group
    async def chat_status(self, event):  # Handler for chat.status
        text_data = json.dumps(event)
        await self.send(text_data)

    async def chat_typing(self, event):  # Handler for chat.typing
        text_data = json.dumps(event)
        await self.send(text_data)

    async def chat_message(self, event):  # Handler for chat.message
        text_data = json.dumps(event)
        await self.send(text_data)

    async def chat_reply(self, event):  # Handler for chat.reply
        text_data = json.dumps(event)
        await self.send(text_data)

    async def chat_audio(self, event):  # Handler for chat.audio
        text_data = json.dumps(event)
        await self.send(text_data)
