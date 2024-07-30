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
from rest_framework.pagination import CursorPagination
from drf_spectacular.utils import extend_schema


class ChatMessagePagination(CursorPagination):
    page_size = 10  # Number of messages per page
    ordering = "-created"



class ChatRoomView(APIView):
    throttle_classes = [UserRateThrottle]
    authentication_classes = [PaletteTokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated, IsChatArtistOrCollector]
    serializer_class = MessageSerializer
    pagination_class = ChatMessagePagination

    @extend_schema(
        operation_id="v1_chat_retrieve",
        tags=["chat_v1"],
    )
    def get(self, request, chat_id):
        """
        Checks if `request.user` is part of the chat, and retrieves the other chat member.
        Supports cursor pagination, which is used to load previous messages unto the chat log.
        Renders `chat.html` with the latest 10 messages in context, along with pagination information, username and status values.
        """
        chat = Chat.objects.select_related("artist__user", "collector__user").filter(id=chat_id).first()
        artist, collector, user = chat.artist.user, chat.collector.user, request.user

        # Retrieve object and online/offline status for other user
        other_user = artist if request.user == collector else collector
        other_user_status = chat.is_artist_online if other_user == artist else chat.is_collector_online
        
        messages = Message.objects.filter(chat=chat).order_by("-created")
        
        # Paginate the messages
        paginator = self.pagination_class()
        paginated_messages = paginator.paginate_queryset(messages, request, view=self)
        messages_list = self.serializer_class(paginated_messages, many=True).data
        
        context = {        
            "chat_id": chat.id,
            "messages": messages_list[::-1],
            "username": user.username,
            "other_user_status": other_user_status,
            "other_username": other_user.username,
            "previous": paginator.get_next_link(),
        }
        
        # Loads previoys messages when the `previous` button is clicked on the F.E.
        if request.headers.get("Accept") == "application/json":
            return Response({
                "results": messages_list,
                "previous": context["previous"]
            })
        return render(request, "chat.html", context)


class ChatList(APIView):
    throttle_classes = [UserRateThrottle]
    authentication_classes = [PaletteTokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="v1_chat_create",
        tags=["chat_v1"],
    )
    def post(self, request, other_user_id):
        """ 
        Creates a new between an artist and a collector.
        Returns a dict of the new chat data.
        """
        current_user = request.user
        other_user = User.objects.filter(id=other_user_id).first()
        if not other_user:
            return Response(
                "Other user does not exist.", status=status.HTTP_404_NOT_FOUND
            )

        artists_list = [str(id) for id in list(Artist.objects.values_list("user_id", flat=True))]
        collectors_list = [str(id) for id in list(Collector.objects.values_list("user_id", flat=True))]
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
        elif all([is_user_collector, is_other_user_artist]):
            artist = Artist.objects.filter(user=other_user).first()
            collector = Collector.objects.filter(user=current_user).first()
            
        new_chat = Chat.objects.create(artist=artist, collector=collector)
        chat_data = ChatSerializer(new_chat).data
        return Response(chat_data, status=status.HTTP_201_CREATED)
