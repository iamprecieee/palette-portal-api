from django.urls import reverse

from .models import Artist, Collector, User

from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.response import Response


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

        self.url1 = reverse("user:jwt-login")

        self.token = self.client.post(
            self.url1, data={"email": self.user1.email, "password": "Test,123"}
        ).data["access"]

    def test_create_chat(self):
        response1 = self.client.post(
            reverse(
                "chat:chat-list",
                kwargs={"other_user_id": "fake-user-id"},
            ),
            headers={"Authorization": f"Bearer {self.token}"},
        )
        self.assertEqual(response1.data, "Badly formed hexadecimal uuid string")

        response2 = self.client.post(
            reverse(
                "chat:chat-list",
                kwargs={"other_user_id": "c63b581d-a57d-4ff0-badf-54e2d0ecfacc"},
            ),
            headers={"Authorization": f"Bearer {self.token}"},
        )
        self.assertEqual(response2.data, "Other user does not exist.")

        response3 = self.client.post(
            reverse(
                "chat:chat-list",
                kwargs={"other_user_id": f"{self.user2.id}"},
            ),
            headers={"Authorization": f"Bearer {self.token}"},
        )
        self.assertEqual(response3.data, "You can only start a chat with a collector.")

        response4 = self.client.post(
            reverse(
                "chat:chat-list",
                kwargs={"other_user_id": f"{self.user3.id}"},
            ),
            headers={"Authorization": f"Bearer {self.token}"},
        )
        self.assertIn("artist", response4.data)
