from django.urls import reverse

from .models import Artist, Collector, User, Message

from rest_framework.test import APITestCase, override_settings
from rest_framework import status
from rest_framework.response import Response
from time import sleep


@override_settings(CELERY_TASK_ALWAYS_EAGER=True, CELERY_TASK_EAGER_PROPAGATES=True)
class ChatRoomTest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            email="user1@gmail.com", username="user1", password="Test,123"
        )
        self.user2 = User.objects.create_user(
            email="user2@gmail.com", username="user2", password="Test,123"
        )
        self.user3 = User.objects.create_user(
            email="user3@gmail.com", username="user3", password="Test,123"
        )
        self.artist1 = Artist.objects.create(user=self.user1)
        self.artist2 = Artist.objects.create(user=self.user2)
        self.collector1 = Collector.objects.create(user=self.user3)

        self.jwt_login = reverse("user:jwt-login")

        self.token = self.client.post(
            self.jwt_login, data={"email": self.user1.email, "password": "Test,123"}
        ).data["access"]
        
        self.token1 = self.client.post(
            self.jwt_login, data={"email": self.user2.email, "password": "Test,123"}
        ).data["access"]
        
        self.chat = self.client.post(
            reverse(
                "chat:chat-list",
                kwargs={"other_user_id": f"{self.user3.id}"},
            ),
            headers={"Authorization": f"Bearer {self.token}"},
        )
        
        for i in range (0, 20):
            Message.objects.create(
                content="Hello",
                sender=self.user1,
                chat_id=self.chat.data["id"]
            )
            Message.objects.create(
                content="Hi",
                sender=self.user3,
                chat_id=self.chat.data["id"]
            )            
        
    def test_get_chatroom_view_success(self):
        response = self.client.get(
            reverse("chat:home", kwargs={"chat_id": self.chat.data["id"]}),
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertTemplateUsed(response, "chat.html")
        
    def test_get_chatroom_view_failure(self):
        response = self.client.get(
            reverse("chat:home", kwargs={"chat_id": "fake-chat-id"}),
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(response.data, '“fake-chat-id” is not a valid UUID.')
        
        response1 = self.client.get(
            reverse("chat:home", kwargs={"chat_id": self.chat.data["id"]}),
            headers={"Authorization": f"Bearer {self.token1}"}
        )
        self.assertEqual(response1.data, "You must be a member of this chat to access it.")
        
        response2 = self.client.get(
            reverse("chat:home", kwargs={"chat_id": "a427abd7-04cf-46d5-b8ed-5bc4742d1686"}),
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(response2.data, "Chat does not exist.")
        
    def tearDown(self):
        super().tearDown()
        sleep(15)


@override_settings(CELERY_TASK_ALWAYS_EAGER=True, CELERY_TASK_EAGER_PROPAGATES=True)
class ChatListTest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            email="user1@gmail.com", username="user1", password="Test,123"
        )
        self.user2 = User.objects.create_user(
            email="user2@gmail.com", username="user2", password="Test,123"
        )
        self.user3 = User.objects.create_user(
            email="user3@gmail.com", username="user3", password="Test,123"
        )
        self.artist1 = Artist.objects.create(user=self.user1)
        self.artist2 = Artist.objects.create(user=self.user2)
        self.collector1 = Collector.objects.create(user=self.user3)

        self.jwt_login = reverse("user:jwt-login")

        self.token = self.client.post(
            self.jwt_login, data={"email": self.user1.email, "password": "Test,123"}
        ).data["access"]

    def test_create_chat_success(self):
        response = self.client.post(
            reverse(
                "chat:chat-list",
                kwargs={"other_user_id": f"{self.user3.id}"},
            ),
            headers={"Authorization": f"Bearer {self.token}"},
        )
        self.assertIn("artist", response.data)
        
    def test_create_chat_failure(self):
        response = self.client.post(
            reverse(
                "chat:chat-list",
                kwargs={"other_user_id": "fake-user-id"},
            ),
            headers={"Authorization": f"Bearer {self.token}"},
        )
        self.assertEqual(response.data, '“fake-user-id” is not a valid UUID.')

        response1 = self.client.post(
            reverse(
                "chat:chat-list",
                kwargs={"other_user_id": "c63b581d-a57d-4ff0-badf-54e2d0ecfacc"},
            ),
            headers={"Authorization": f"Bearer {self.token}"},
        )
        self.assertEqual(response1.data, "Other user does not exist.")

        response2 = self.client.post(
            reverse(
                "chat:chat-list",
                kwargs={"other_user_id": f"{self.user2.id}"},
            ),
            headers={"Authorization": f"Bearer {self.token}"},
        )
        self.assertEqual(response2.data, "You can only start a chat with a collector.")
        
    def tearDown(self):
        super().tearDown()
        sleep(15)
