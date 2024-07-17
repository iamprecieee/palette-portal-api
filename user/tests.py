from django.urls import reverse
from django.core.cache import cache

from .models import User, Artist, Collector, PaletteAuthToken

from rest_framework.test import APITestCase
from time import sleep


class RegisterViewTestCase(APITestCase):
    def setUp(self):
        self.url = reverse("user:register")
        
    def test_register_success(self):
        response = self.client.post(self.url, data={
            "email": "admin@gmail.com",
            "username": "admin",
            "password": "Admin,123",
            "confirm_password": "Admin,123"
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn("email", response.data)
        
    def test_register_failures(self):
        User.objects.create_user(
            email="admin@gmail.com",
            username="admin",
            password="Admin,123"
        )
        
        response1 = self.client.post(self.url, data={
            "email": "admin@gmail.com",
            "username": "admin1",
            "password": "Admin123",
            "confirm_password": "Admin,123"
        })
        self.assertEqual(response1.status_code, 400)
        self.assertEqual(response1.data, "User with this email already exists.")
        
        
        response2 = self.client.post(self.url, data={
            "email": "admin1@gmail.com",
            "username": "admin1",
            "password": "Admin123",
            "confirm_password": "Admin,123"
        })
        self.assertEqual(response2.status_code, 400)
        self.assertEqual(response2.data, "Password error. Password must contain at least 1 symbol.")
        
    def tearDown(self):
        super().tearDown()
        sleep(15)
    
    
class LoginViewTestCase(APITestCase):
    def setUp(self):
        self.knox_login = reverse("user:knox-login")
        self.jwt_login = reverse("user:jwt-login")
        self.mock_url = reverse("user:mock-login")
        self.refresh_url = reverse("user:token-refresh")
        self.knox_logout = reverse("user:knox-logout")
        self.jwt_logout = reverse("user:jwt-logout")
        self.knox_batch_logout = reverse("user:batch-knox-logout")
        User.objects.create_user(
            email="admin@gmail.com",
            username="admin",
            password="Admin,123"
        )
    
    def test_knox_login_success(self):
        for i in range(1, 5):
            response = self.client.post(self.knox_login, data={
                "email": "admin@gmail.com",
                "password": "Admin,123"
            })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(list(PaletteAuthToken.objects.values_list("digest", flat=True))), 3)
        self.assertIn("token", response.data.keys())
        
    def test_knox_login_failure(self):
        response = self.client.post(self.knox_login, data={
            "email": "admin1@gmail.com",
            "password": "Admin,123"
        })
        self.assertEqual(response.status_code, 401)
        self.assertEqual("No active account found with the given credentials.", response.data)
        
    def test_jwt_login_success(self):
        response = self.client.post(self.jwt_login, data={
                "email": "admin@gmail.com",
                "password": "Admin,123"
            })
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data.keys())

    def test_jwt_login(self):
        response = self.client.post(self.jwt_login, data={
            "email": "admin1@gmail.com",
            "password": "Admin,123"
        })
        self.assertEqual(response.status_code, 401)
        self.assertEqual("No active account found with the given credentials", response.data)
        
        
    def test_jwt_token_refresh_success(self):
        response = self.client.post(self.jwt_login, data={
                "email": "admin@gmail.com",
                "password": "Admin,123"
            })
        response1 = self.client.post(self.refresh_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["refresh"], response1.data["refresh"])
        self.assertIn("access", response1.data.keys())
        
    def test_mock_login(self):
        response = self.client.post(self.knox_login, data={
            "email": "admin@gmail.com",
            "password": "Admin,123"
        })
        token = response.data["token"]
        response1 = self.client.get(self.mock_url, headers={"Authorization": f"Token {token}"})
        self.assertEqual("Hello world.", response1.data)
        
        response2 = self.client.post(self.jwt_login, data={
            "email": "admin@gmail.com",
            "password": "Admin,123"
        })
        token = response2.data["access"]
        response3 = self.client.get(self.mock_url, headers={"Authorization": f"Bearer {token}"})
        self.assertEqual("Hello world.", response3.data)

    def test_knox_logout_success(self):
        response = self.client.post(self.knox_login, data={
            "email": "admin@gmail.com",
            "password": "Admin,123"
        })
        token = response.data["token"]
        self.client.post(self.knox_logout, headers={"Authorization": f"Token {token}"})
        response1 = self.client.get(self.knox_logout, headers={"Authorization": f"Token {token}"})
        self.assertEqual("Invalid token.", response1.data)
        
    def test_jwt_logout_success(self):
        response = self.client.post(self.jwt_login, data={
            "email": "admin@gmail.com",
            "password": "Admin,123"
        })
        token = response.data["access"]
        self.client.post(self.jwt_logout, headers={"Authorization": f"Bearer {token}"})
        response1 = self.client.get(self.jwt_logout, headers={"Authorization": f"Bearer {token}"})
        self.assertEqual("Invalid token.", response1.data)

    def test_batch_knox_logout_success(self):
        token_list = {}
        for i in range(0,3):
            response = self.client.post(self.knox_login, data={
                "email": "admin@gmail.com",
                "password": "Admin,123"
            })
            if "token" in response.data.keys():
                token_list.update({f"token{i}": response.data["token"]})
        self.assertEqual(3, len(token_list.keys()))
        response1 = self.client.post(
            self.knox_batch_logout,
            headers={"Authorization": f"Token {token_list["token0"]}"}
        )
        self.assertEqual("Batch logout successful.", response1.data)
        response2 = self.client.post(
            self.knox_logout,
            headers={"Authorization": f"Token {token_list["token1"]}"}
        )
        self.assertEqual("Invalid token.", response2.data)
    
    def tearDown(self):
        super().tearDown()
        sleep(15)
    
    
class ArtistProfileViewTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            email="admin1@gmail.com",
            username="admin1",
            password="Admin,123"
        )
        self.user2 = User.objects.create_user(
            email="admin2@gmail.com",
            username="admin2",
            password="Admin,123"
        )
        self.user3 = User.objects.create_user(
            email="admin3@gmail.com",
            username="admin3",
            password="Admin,123"
        )
        self.artist1 = Artist.objects.create(
            user=self.user1
        )
        self.artist2 = Artist.objects.create(
            user=self.user2
        )
        
        self.knox_login = reverse("user:knox-login")
        self.artist_profile = reverse("user:artist-profile-list")
        self.artist1_detail = reverse("user:artist-profile-detail", kwargs={
            "profile_id": self.artist1.id
        })
        self.artist3_detail = reverse("user:artist-profile-detail", kwargs={
            "profile_id": "764e3e7c-3c23-4f06-8a48-ef37abf3b8cf"
        })

    def test_get_artists_from_db_success(self):
        cache.clear()
        self.assertIsNone(cache.get("artist_list"))
        
        response = self.client.post(
            self.knox_login,
            data={"email": "admin1@gmail.com", "password": "Admin,123"}
        )
        token = response.data["token"]
        self.client.get(
            self.artist_profile,
            headers={"Authorization": f"Token {token}"}
        )
        # Checks that queries are cached properly
        self.assertIsNotNone(cache.get("artist_list"))
        cache.clear()

        response1 = self.client.get(
            self.artist_profile,
            headers={"Authorization": f"Token {token}"}
        )
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(len(response1.data), 2)
        self.assertEqual(response1.data[0]["id"], str(self.artist2.id))
        self.assertIsNotNone(cache.get("artist_list"))
        
    def test_get_collectors_from_cache_success(self):
        artist = Artist.objects.create(user=self.user3)
        cache.set("artist_list", [artist])
        
        response = self.client.post(
            self.knox_login,
            data={"email": "admin1@gmail.com", "password": "Admin,123"}
        )
        token = response.data["token"]
        response1 = self.client.get(
            self.artist_profile,
            headers={"Authorization": f"Token {token}"}
        )
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(len(response1.data), 1)
        self.assertEqual(response1.data[0]["id"], str(artist.id))
        
    def test_artist_profile_list_get_failure(self):
        response = self.client.get(self.artist_profile)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data, "Authentication credentials were not provided.")

    def test_artist_profile_list_post_success(self):
        response = self.client.post(
            self.knox_login,
            data={"email": "admin3@gmail.com", "password": "Admin,123"}
        )
        token = response.data["token"]
        response1 = self.client.post(
            self.artist_profile,
            data={"bio": "Just making art."},
            headers={"Authorization": f"Token {token}"}
        )
        self.assertIn("user", response1.data)
        self.assertEqual(response1.status_code, 201)
        
    def test_artist_profile_list_post_failure(self):
        response = self.client.post(self.knox_login)
        response1 = self.client.post(
            self.artist_profile,
            data={"bio": "Just making art."}
        )
        self.assertEqual("Authentication credentials were not provided.", response1.data)
        self.assertEqual(response1.status_code, 401)
        
        response = self.client.post(
            self.knox_login,
            data={"email": "admin2@gmail.com", "password": "Admin,123"}
        )
        token = response.data["token"]
        response1 = self.client.post(
            self.artist_profile,
            data={"bio": "Just making art."},
            headers={"Authorization": f"Token {token}"}
        )
        self.assertEqual("This user has an existing artist profile.", response1.data)
        self.assertEqual(response1.status_code, 409)
    
    def test_artist_profile_detail_get_success(self):
        response = self.client.post(
            self.knox_login,
            data={"email": "admin1@gmail.com", "password": "Admin,123"}
        )
        token = response.data["token"]
        response1 = self.client.get(
            self.artist1_detail,
            headers={"Authorization": f"Token {token}"}
        )
        self.assertIn("user", response1.data)
        self.assertEqual(response1.status_code, 200)
        
    def test_artist_profile_detail_get_failure(self):
        response = self.client.post(
            self.knox_login,
            data={"email": "admin1@gmail.com", "password": "Admin,123"}
        )
        token = response.data["token"]
        response1 = self.client.get(
            self.artist3_detail,
            headers={"Authorization": f"Token {token}"}
        )
        self.assertEqual("Profile does not exist.", response1.data)
        self.assertEqual(response1.status_code, 404)
        
    def test_artist_profile_detail_put_success(self):
        response = self.client.post(
            self.knox_login,
            data={"email": "admin1@gmail.com", "password": "Admin,123"}
        )
        token = response.data["token"]
        response1 = self.client.put(
            self.artist1_detail,
            data={"bio": "Making more art"},
            headers={"Authorization": f"Token {token}"}
        )
        self.assertEqual("Making more art", response1.data["bio"])
        self.assertEqual(response1.status_code, 202)
        
    def test_artist_profile_detail_put_failure(self):
        response = self.client.post(
            self.knox_login,
            data={"email": "admin3@gmail.com", "password": "Admin,123"}
        )
        token = response.data["token"]
        response1 = self.client.put(
            self.artist1_detail,
            data={"bio": "Making more art"},
            headers={"Authorization": f"Token {token}"}
        )
        self.assertEqual("You are not allowed to operate on another user's profile.", response1.data)
        self.assertEqual(response1.status_code, 403)
        
        response2 = self.client.post(
            self.knox_login,
            data={"email": "admin1@gmail.com", "password": "Admin,123"}
        )
        token = response2.data["token"]
        response3 = self.client.put(
            self.artist3_detail,
            headers={"Authorization": f"Token {token}"}
        )
        self.assertEqual("Profile does not exist.", response3.data)
        self.assertEqual(response3.status_code, 404)
        
    def test_artist_profile_detail_delete_success(self):
        response = self.client.post(
            self.knox_login,
            data={"email": "admin1@gmail.com", "password": "Admin,123"}
        )
        token = response.data["token"]
        response1 = self.client.delete(
            self.artist1_detail,
            data={"bio": "Making more art"},
            headers={"Authorization": f"Token {token}"}
        )
        self.assertIsNone(response1.data)
        self.assertEqual(response1.status_code, 204)
        
    def test_artist_profile_detail_delete_failure(self):
        response = self.client.post(
            self.knox_login,
            data={"email": "admin3@gmail.com", "password": "Admin,123"}
        )
        token = response.data["token"]
        response1 = self.client.delete(
            self.artist1_detail,
            headers={"Authorization": f"Token {token}"}
        )
        self.assertEqual("You are not allowed to operate on another user's profile.", response1.data)
        self.assertEqual(response1.status_code, 403)
        
        response2 = self.client.post(
            self.knox_login,
            data={"email": "admin1@gmail.com", "password": "Admin,123"}
        )
        token = response2.data["token"]
        response3 = self.client.delete(
            self.artist3_detail,
            headers={"Authorization": f"Token {token}"}
        )
        self.assertEqual("Profile does not exist.", response3.data)
        self.assertEqual(response3.status_code, 404)
        
    def tearDown(self):
        super().tearDown()
        sleep(15)


class CollectorProfileViewTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            email="admin1@gmail.com",
            username="admin1",
            password="Admin,123"
        )
        self.user2 = User.objects.create_user(
            email="admin2@gmail.com",
            username="admin2",
            password="Admin,123"
        )
        self.user3 = User.objects.create_user(
            email="admin3@gmail.com",
            username="admin3",
            password="Admin,123"
        )
        self.collector1 = Collector.objects.create(
            user=self.user1
        )
        self.collector2 = Collector.objects.create(
            user=self.user2
        )
        
        self.knox_login = reverse("user:knox-login")
        self.collector_profile = reverse("user:collector-profile-list")
        self.collector1_detail = reverse("user:collector-profile-detail", kwargs={
            "profile_id": self.collector1.id
        })
        self.collector3_detail = reverse("user:collector-profile-detail", kwargs={
            "profile_id": "764e3e7c-3c23-4f06-8a48-ef37abf3b8cf"
        })

    def test_get_collectors_from_db_success(self):
        cache.clear()
        self.assertIsNone(cache.get("collector_list"))
        
        response = self.client.post(
            self.knox_login,
            data={"email": "admin1@gmail.com", "password": "Admin,123"}
        )
        token = response.data["token"]
        self.client.get(
            self.collector_profile,
            headers={"Authorization": f"Token {token}"}
        )
        # Checks that queries are cached properly
        self.assertIsNotNone(cache.get("collector_list"))
        cache.clear()

        response1 = self.client.get(
            self.collector_profile,
            headers={"Authorization": f"Token {token}"}
        )
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(len(response1.data), 2)
        self.assertEqual(response1.data[0]["id"], str(self.collector2.id))
        self.assertIsNotNone(cache.get("collector_list"))
        
    def test_get_collectors_from_cache_success(self):
        collector = Collector.objects.create(user=self.user3)
        cache.set("collector_list", [collector])
        
        response = self.client.post(
            self.knox_login,
            data={"email": "admin1@gmail.com", "password": "Admin,123"}
        )
        token = response.data["token"]
        response1 = self.client.get(
            self.collector_profile,
            headers={"Authorization": f"Token {token}"}
        )
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(len(response1.data), 1)
        self.assertEqual(response1.data[0]["id"], str(collector.id))
        
    def test_collector_profile_list_get_failure(self):
        response = self.client.get(self.collector_profile)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data, "Authentication credentials were not provided.")

    def test_collector_profile_list_post_success(self):
        response = self.client.post(
            self.knox_login,
            data={"email": "admin3@gmail.com", "password": "Admin,123"}
        )
        token = response.data["token"]
        response1 = self.client.post(
            self.collector_profile,
            data={"bio": "Just buying art."},
            headers={"Authorization": f"Token {token}"}
        )
        self.assertIn("user", response1.data)
        self.assertEqual(response1.status_code, 201)
        
    def test_collector_profile_list_post_failure(self):
        response = self.client.post(self.knox_login)
        response1 = self.client.post(
            self.collector_profile,
            data={"bio": "Just buying art."}
        )
        self.assertEqual("Authentication credentials were not provided.", response1.data)
        self.assertEqual(response1.status_code, 401)
        
        response = self.client.post(
            self.knox_login,
            data={"email": "admin2@gmail.com", "password": "Admin,123"}
        )
        token = response.data["token"]
        response1 = self.client.post(
            self.collector_profile,
            data={"bio": "Just buying art."},
            headers={"Authorization": f"Token {token}"}
        )
        self.assertEqual("This user has an existing collector profile.", response1.data)
        self.assertEqual(response1.status_code, 409)
    
    def test_collector_profile_detail_get_success(self):
        response = self.client.post(
            self.knox_login,
            data={"email": "admin1@gmail.com", "password": "Admin,123"}
        )
        token = response.data["token"]
        response1 = self.client.get(
            self.collector1_detail,
            headers={"Authorization": f"Token {token}"}
        )
        self.assertIn("user", response1.data)
        self.assertEqual(response1.status_code, 200)
        
    def test_collector_profile_detail_get_failure(self):
        response = self.client.post(
            self.knox_login,
            data={"email": "admin1@gmail.com", "password": "Admin,123"}
        )
        token = response.data["token"]
        response1 = self.client.get(
            self.collector3_detail,
            headers={"Authorization": f"Token {token}"}
        )
        self.assertEqual("Profile does not exist.", response1.data)
        self.assertEqual(response1.status_code, 404)
        
    def test_collector_profile_detail_put_success(self):
        response = self.client.post(
            self.knox_login,
            data={"email": "admin1@gmail.com", "password": "Admin,123"}
        )
        token = response.data["token"]
        response1 = self.client.put(
            self.collector1_detail,
            data={"bio": "Buying more art"},
            headers={"Authorization": f"Token {token}"}
        )
        self.assertEqual("Buying more art", response1.data["bio"])
        self.assertEqual(response1.status_code, 202)
        
    def test_collector_profile_detail_put_failure(self):
        response = self.client.post(
            self.knox_login,
            data={"email": "admin3@gmail.com", "password": "Admin,123"}
        )
        token = response.data["token"]
        response1 = self.client.put(
            self.collector1_detail,
            data={"bio": "Buying more art"},
            headers={"Authorization": f"Token {token}"}
        )
        self.assertEqual("You are not allowed to operate on another user's profile.", response1.data)
        self.assertEqual(response1.status_code, 403)
        
        response2 = self.client.post(
            self.knox_login,
            data={"email": "admin1@gmail.com", "password": "Admin,123"}
        )
        token = response2.data["token"]
        response3 = self.client.put(
            self.collector3_detail,
            headers={"Authorization": f"Token {token}"}
        )
        self.assertEqual("Profile does not exist.", response3.data)
        self.assertEqual(response3.status_code, 404)
        
    def test_collector_profile_detail_delete_success(self):
        response = self.client.post(
            self.knox_login,
            data={"email": "admin1@gmail.com", "password": "Admin,123"}
        )
        token = response.data["token"]
        response1 = self.client.delete(
            self.collector1_detail,
            data={"bio": "Buying more art"},
            headers={"Authorization": f"Token {token}"}
        )
        self.assertIsNone(response1.data)
        self.assertEqual(response1.status_code, 204)
        
    def test_collector_profile_detail_delete_failure(self):
        response = self.client.post(
            self.knox_login,
            data={"email": "admin3@gmail.com", "password": "Admin,123"}
        )
        token = response.data["token"]
        response1 = self.client.delete(
            self.collector1_detail,
            headers={"Authorization": f"Token {token}"}
        )
        self.assertEqual("You are not allowed to operate on another user's profile.", response1.data)
        self.assertEqual(response1.status_code, 403)
        
        response2 = self.client.post(
            self.knox_login,
            data={"email": "admin1@gmail.com", "password": "Admin,123"}
        )
        token = response2.data["token"]
        response3 = self.client.delete(
            self.collector3_detail,
            headers={"Authorization": f"Token {token}"}
        )
        self.assertEqual("Profile does not exist.", response3.data)
        self.assertEqual(response3.status_code, 404)
        
    def tearDown(self):
        super().tearDown()
        sleep(15)