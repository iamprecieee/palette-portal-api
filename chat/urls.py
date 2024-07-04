from django.urls import path

from .views import ChatRoomView


app_name = "chat"

urlpatterns = [
    path("<uuid:chat_id>/", ChatRoomView.as_view(), name="home"),
]
