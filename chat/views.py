from django.shortcuts import render

from user.views import (
    APIView,
    Response,
    status,
    IsAuthenticated,
    UserRateThrottle,
    JWTAuthentication,
    PaletteTokenAuthentication,
)
from .models import Chat, Message
from .serializers import MessageSerializer


class ChatRoomView(APIView):
    throttle_classes = [UserRateThrottle]
    authentication_classes = [PaletteTokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def get(self, request, chat_id):
        """
        Checks if `request.user` is part of the chat, and retrieves the other chat member.
        Sends the latest 20 messages in context, including the username values.
        """
        chat = Chat.objects.filter(id=chat_id).first()
        if not chat:
            return Response("Chat does not exist.", status=status.HTTP_404_NOT_FOUND)

        artist = chat.artist.user
        collector = chat.collector.user
        user = request.user
        if not user in (artist, collector):
            return Response(
                "You are not part of this chat.", status=status.HTTP_401_UNAUTHORIZED
            )

        # Retrieve object and online/offline status for other user
        other_user = artist if request.user == collector else collector
        other_user_status = (
            chat.is_artist_online if other_user == artist else chat.is_collector_online
        )

        messages = Message.objects.filter(chat=chat)[:30]

        # Retain the order of messages
        messages_list = self.serializer_class(messages, many=True).data[::-1]

        return render(
            request,
            "chat.html",
            {
                "chat_id": chat.id,
                "messages": messages_list,
                "username": user.username,
                "other_user_status": other_user_status,
                "other_username": other_user.username,
            },
        )
