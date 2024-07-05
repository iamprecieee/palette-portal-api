from django.utils.dateformat import format

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

        headers = dict(
            self.scope["headers"]
        )  # Headers dict should contain the authentication token
        user = await confirm_authorization(headers)
        self.user = user
        self.username = user.username
        chat = await get_chat_members(
            self.chat_id
        )  # Retrieves the users in the current chat
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
            {"type": "chat.status", "content": "offline", "username": self.username},
        )

        await self.channel_layer.group_discard(self.chat_group_name, self.channel_name)

        await set_user_status(self.user, self.chat_id, status="offline")

    # Receive message from websocket client
    async def receive(self, text_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json.get("message")
        message_type = text_data_json.get("type")

        # Send message to chat group
        if message_type == "typing":
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

        elif message_type == "reply":
            previous_message_id = text_data_json.get("previous_message_id")
            if message:
                replied_message = await get_replied_message(previous_message_id, self.chat_id)
                reply_id, created = await create_new_reply(
                    self.user,
                    message,
                    replied_message["sender"],
                    replied_message["content"],
                    previous_message_id,
                    self.chat_id,
                )

                await self.channel_layer.group_send(
                    self.chat_group_name,
                    {
                        "type": "chat.reply",
                        "content": message,
                        "previous_sender": replied_message["sender"],
                        "previous_content": replied_message["content"],
                        "previous_message_id": previous_message_id,
                        "time": format(created, "P"),
                        "sender": self.username,
                        "id": str(reply_id)
                    },
                )

        else:
            if message:
                message_id, created = await create_new_message(self.user, message, self.chat_id)

                await self.channel_layer.group_send(
                    self.chat_group_name,
                    {
                        "type": "chat.message",
                        "content": message,
                        "created": format(created, "M. d, Y"),
                        "time": format(created, "P"),
                        "sender": self.username,
                        "id": str(message_id)
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
