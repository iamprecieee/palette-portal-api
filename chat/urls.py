from django.urls import path

from .views import ChatRoomView, ChatList


app_name = "chat"

urlpatterns = [
    path("<str:chat_id>/", ChatRoomView.as_view(), name="home"),
    path("list/<str:other_user_id>/", ChatList.as_view(), name="chat-list"),
]
