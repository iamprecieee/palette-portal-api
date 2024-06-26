from django.urls import reverse

from .models import User, PaletteAuthToken

from rest_framework.test import APITestCase


class RegisterLoginLogoutTestCase(APITestCase):
    def setUp(self):
        self.url = reverse("user:register")
        self.url1 = reverse("user:knox-login")
        self.url2 = reverse("user:jwt-login")
        self.url3 = reverse("user:mock-login")
        self.url4 = reverse("user:token-refresh")
        self.url5 = reverse("user:knox-logout")
        self.url6 = reverse("user:jwt-logout")
        self.url7 = reverse("user:batch-knox-logout")
        
        User.objects.create_user(
            email="admin@gmail.com",
            username="admin",
            password="Admin,123"
        )
        
    def test_register(self):
        response = self.client.post(self.url, data={
            "email": "admin1@gmail.com",
            "username": "admin",
            "password": "Admin,123",
            "confirm_password": "Admin,123"
        })
        
        self.assertEqual("User with this username already exists.", response.data)
        
        response1 = self.client.post(self.url, data={
            "email": "admin1@gmail.com",
            "username": "admin1",
            "password": "Admin123",
            "confirm_password": "Admin,123"
        })
        
        self.assertEqual("Password error. Password must contain at least 1 symbol.", response1.data)
        
        response2 = self.client.post(self.url, data={
            "email": "admin2@gmail.com",
            "username": "admin2",
            "password": "Admin,123",
            "confirm_password": "Admin,123"
        })
        
        self.assertIn("admin2@gmail.com", response2.data.values())
        
    def test_knox_login(self):
        response = self.client.post(self.url1, data={
            "email": "admin1@gmail.com",
            "password": "Admin,123"
        })
        
        self.assertEqual("No active account found with the given credentials.", response.data)
        
        for i in range(1, 5):
            response1 = self.client.post(self.url1, data={
                "email": "admin@gmail.com",
                "password": "Admin,123"
            })
            
        self.assertEqual(len(list(PaletteAuthToken.objects.values_list("digest", flat=True))), 3)
        
        self.assertIn("token", response1.data.keys())
        
    def test_jwt_login(self):
        response = self.client.post(self.url2, data={
            "email": "admin1@gmail.com",
            "password": "Admin,123"
        })
        
        self.assertEqual("No active account found with the given credentials", response.data)
        
        response1 = self.client.post(self.url2, data={
                "email": "admin@gmail.com",
                "password": "Admin,123"
            })
        
        self.assertIn("access", response1.data.keys())
        
    def test_token_refresh(self):
        response = self.client.post(self.url2, data={
                "email": "admin@gmail.com",
                "password": "Admin,123"
            })
        
        response1 = self.client.post(self.url4)
        
        self.assertIn("access", response1.data.keys())
        
    def test_mock_login(self):
        response = self.client.post(self.url1, data={
            "email": "admin@gmail.com",
            "password": "Admin,123"
        })
        
        token = response.data["token"]
        
        response1 = self.client.get(self.url3, headers={"Authorization": f"Token {token}"})
        
        self.assertEqual("Hello world.", response1.data)
        
        response2 = self.client.post(self.url2, data={
            "email": "admin@gmail.com",
            "password": "Admin,123"
        })
        
        token = response2.data["access"]
        
        response3 = self.client.get(self.url3, headers={"Authorization": f"Bearer {token}"})
        
        self.assertEqual("Hello world.", response3.data)
        
    def test_logout(self):
        response = self.client.post(self.url1, data={
            "email": "admin@gmail.com",
            "password": "Admin,123"
        })
        
        token = response.data["token"]
        
        self.client.post(self.url5, headers={"Authorization": f"Token {token}"})
        
        response2 = self.client.get(self.url3, headers={"Authorization": f"Token {token}"})
        
        self.assertEqual("Invalid token.", response2.data)
        
        response3 = self.client.post(self.url2, data={
            "email": "admin@gmail.com",
            "password": "Admin,123"
        })
        
        token = response3.data["access"]
        
        self.client.post(self.url6, headers={"Authorization": f"Bearer {token}"})
        
        response4 = self.client.get(self.url3, headers={"Authorization": f"Bearer {token}"})
        
        self.assertEqual("Invalid token.", response4.data)

    def test_batch_knox_logout(self):
        token_list = {}
        for i in range(0,3):
            response = self.client.post(self.url1, data={
                "email": "admin@gmail.com",
                "password": "Admin,123"
            })
            if "token" in response.data.keys():
                token_list.update({f"token{i}": response.data["token"]})

        self.assertEqual(3, len(token_list.keys()))
        
        response1 = self.client.post(self.url7,
                                     headers={"Authorization": f"Token {token_list["token0"]}"})
        
        self.assertEqual("Batch logout successful.", response1.data)
        
        response2 = self.client.post(self.url3,
                                     headers={"Authorization": f"Token {token_list["token1"]}"})
        
        self.assertEqual("Invalid token.", response2.data)
    
    
class ProfileTestCase(APITestCase):
    def setUp(self):
        User.objects.create_user(
            email="admin@gmail.com",
            username="admin",
            password="Admin,123"
        )
        
        self.url = reverse("user:knox-login")
        self.url1 = reverse("user:artist-profile-list")
        self.url2 = reverse("user:collector-profile-list")
        
    def test_artist_list_get_post(self):
        response = self.client.post(self.url, data={
                "email": "admin@gmail.com",
                "password": "Admin,123"
            })
        
        token = response.data["token"]
        
        response1 = self.client.post(self.url1, 
                                    headers={"Authorization": f"Token {token}"},
                                     data={"bio": "Just making art."})
        
        self.assertIn("user", response1.data)
        
        response2 = self.client.get(self.url1, 
                                    headers={"Authorization": f"Token {token}"})
        
        self.assertIn("user", response2.data[0])
        
        response3 = self.client.post(self.url1, 
                                    headers={"Authorization": f"Token {token}"},
                                     data={"bio": "Just making art."})
        
        self.assertEqual("This user has an existing artist profile.", response3.data)
        
        
    def test_collector_list_get_post(self):
        response = self.client.post(self.url, data={
                "email": "admin@gmail.com",
                "password": "Admin,123"
            })
        
        token = response.data["token"]
        
        response1 = self.client.post(self.url2, 
                                    headers={"Authorization": f"Token {token}"},
                                        data={"bio": "Just collecting art."})
        
        self.assertIn("user", response1.data)
        
        response2 = self.client.get(self.url2, 
                                    headers={"Authorization": f"Token {token}"})
        
        self.assertIn("user", response2.data[0])
        
        response3 = self.client.post(self.url2, 
                                    headers={"Authorization": f"Token {token}"},
                                        data={"bio": "Just collecting art."})
        
        self.assertEqual("This user has an existing collector profile.", response3.data)
        