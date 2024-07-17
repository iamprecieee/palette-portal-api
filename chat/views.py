from django.shortcuts import render

from user.views import (
    APIView,
    Response,
    status,
    IsAuthenticated,
    UserRateThrottle,
    JWTAuthentication,
    PaletteTokenAuthentication,
    User,
    Artist,
    Collector,
)
from .models import Chat, Message
from .serializers import MessageSerializer, ChatSerializer
from portal.permissions import IsChatArtistOrCollector

from uuid import UUID


class ChatRoomView(APIView):
    throttle_classes = [UserRateThrottle]
    authentication_classes = [PaletteTokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated, IsChatArtistOrCollector]
    serializer_class = MessageSerializer

    def get(self, request, chat_id):
        """
        Checks if `request.user` is part of the chat, and retrieves the other chat member.
        Sends the latest 20 messages in context, including the username values.
        """
        chat = Chat.objects.filter(id=chat_id).first()
        artist = chat.artist.user
        collector = chat.collector.user
        user = request.user

        # Retrieve object and online/offline status for other user
        other_user = artist if request.user == collector else collector
        other_user_status = chat.is_artist_online if other_user == artist else chat.is_collector_online

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


class ChatList(APIView):
    throttle_classes = [UserRateThrottle]
    authentication_classes = [PaletteTokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, other_user_id):
        current_user = request.user
        other_user = User.objects.filter(id=other_user_id).first()
        if not other_user:
            return Response(
                "Other user does not exist.", status=status.HTTP_404_NOT_FOUND
            )

        artists_list = [
            str(id) for id in list(Artist.objects.values_list("user_id", flat=True))
        ]
        collectors_list = [
            str(id) for id in list(Collector.objects.values_list("user_id", flat=True))
        ]
        is_user_artist = str(current_user.id) in artists_list
        is_user_collector = str(current_user.id) in collectors_list
        is_other_user_artist = str(other_user.id) in artists_list
        is_other_user_collector = str(other_user.id) in collectors_list

        if all([is_user_artist, is_other_user_artist]):
            return Response(
                "You can only start a chat with a collector.",
                status=status.HTTP_403_FORBIDDEN,
            )

        if all([is_user_collector, is_other_user_collector]):
            return Response(
                "You can only start a chat with an artist.",
                status=status.HTTP_403_FORBIDDEN,
            )

        new_chat = None
        if all([is_user_artist, is_other_user_collector]):
            artist = Artist.objects.filter(user=current_user).first()
            collector = Collector.objects.filter(user=other_user).first()
            new_chat = Chat.objects.create(artist=artist, collector=collector)
        elif all([is_user_collector, is_other_user_artist]):
            artist = Artist.objects.filter(user=other_user).first()
            collector = Collector.objects.filter(user=current_user).first()
            new_chat = Chat.objects.create(artist=artist, collector=collector)

        chat_data = ChatSerializer(new_chat).data

        return Response(chat_data, status=status.HTTP_201_CREATED)
