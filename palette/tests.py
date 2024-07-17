from django.urls import reverse
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.contrib.auth import get_user_model

from .models import Genre, Artwork
from .cart import Cart
from user.models import Artist, Collector

from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework import status
from cloudinary.api import resource
import os
from time import sleep


User = get_user_model()
static_dir = settings.STATICFILES_DIRS[0]
image_file = settings.BASE_DIR/"static/image/test.png"


# class GenreListTestViewCase(APITestCase):
#     def setUp(self):
#         self.user1 = User.objects.create_superuser(
#             email="user1@gmail.com", username="user1", password="Test,123"
#         )
#         self.user2 = User.objects.create_user(
#             email="user2@gmail.com", username="user2", password="Test,123"
#         )
        
#         self.genre_list = reverse("palette:genre-list")
#         self.jwt_login = reverse("user:jwt-login")
        
#         self.token = self.client.post(
#             self.jwt_login, data={"email": self.user1.email, "password": "Test,123"}
#         )
#         self.token1 = self.client.post(
#             self.jwt_login, data={"email": self.user2.email, "password": "Test,123"}
#         )
        
#         Genre.objects.create(name="Genre")

#     def test_get_genres_from_db_success(self):
#         genre = Genre.objects.create(name="Abstract")
#         cache.clear()

#         # Anonymous user
#         self.client.get(self.genre_list)
#         self.assertIsNotNone(cache.get("genre_list"))
        
#         # Logged-in user
#         self.client.get(
#             self.genre_list,
#             headers={"Authorization": f"Bearer {self.token.data["access"]}"}
#         )
#         # Checks that queries are cached properly
#         self.assertIsNotNone(cache.get("genre_list"))
#         cache.clear()

#         response1 = self.client.get(
#             self.genre_list,
#             headers={"Authorization": f"Bearer {self.token.data["access"]}"}
#         )
#         self.assertEqual(response1.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response1.data), 1)
#         self.assertEqual(response1.data[0]["name"], genre.name)
#         self.assertIsNotNone(cache.get("genre_list"))

#     def test_get_genres_from_cache_success(self):
#         genre = Genre.objects.create(name="Vector")
#         cache.set("genre_list", [genre])
        
#         response = self.client.get(self.genre_list)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 1)
#         self.assertEqual(response.data[0]["name"], genre.name)

#         response1 = self.client.get(
#             self.genre_list,
#             headers={"Authorization": f"Bearer {self.token.data["access"]}"}
#         )
#         self.assertEqual(response1.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response1.data), 1)
#         self.assertEqual(response1.data[0]["name"], genre.name)

#     def test_create_genre_success(self):
#         data = {"name": "Cubism"}

#         response = self.client.post(
#             self.genre_list,
#             data,
#             headers={"Authorization": f"Bearer {self.token.data["access"]}"}   
#         )
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(Genre.objects.count(), 1)
#         self.assertEqual(Genre.objects.get().name, "Cubism")

#     def test_create_genre_failure(self):
#         data = {"name": ""}

#         response = self.client.post(
#             self.genre_list,
#             data,
#             headers={"Authorization": f"Bearer {self.token.data["access"]}"}   
#         )
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual("Name field cannot be blank.", response.data)
        
#         response1 = self.client.post(
#             self.genre_list,
#             data,
#             headers={"Authorization": f"Bearer {self.token1.data["access"]}"}   
#         )
#         self.assertEqual(response1.status_code, status.HTTP_403_FORBIDDEN)
#         self.assertEqual("You must be an admin to perform this action.", response1.data)
        
#         response2 = self.client.post(
#             self.genre_list,
#             data  
#         )
#         self.assertEqual(response2.status_code, status.HTTP_401_UNAUTHORIZED)
        
#         response3 = self.client.post(
#             self.genre_list,
#             data= {"name": "Genre"},
#             headers={"Authorization": f"Bearer {self.token.data["access"]}"}   
#         )
#         self.assertEqual(response3.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response3.data, "Genre with this name already exists.")
        
#     def test_throttling(self):
#         for i in range(0, 11):
#             response = self.client.get(
#                 self.url
#             )

#         self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
#         self.assertIn("Request was throttled", response.data)
        
#         for i in range(0, 21):
#             response1 = self.client.get(
#                 self.url,
#                 headers={"Authorization": f"Bearer {self.token.data["access"]}"}
#             )

#         self.assertEqual(response1.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
#         self.assertIn("Request was throttled", response1.data)
        
#     def tearDown(self):
#         super().tearDown()
#         sleep(15)


# class GenreDetailViewTestCase(APITestCase):
#     def setUp(self):
#         self.user1 = User.objects.create_superuser(
#             email="user1@gmail.com", username="user1", password="Test,123"
#         )
#         self.user2 = User.objects.create_user(
#             email="user2@gmail.com", username="user2", password="Test,123"
#         )
        
#         self.genre = Genre.objects.create(name="Abstract", slug="abstract")
#         self.genre_detail = reverse("palette:genre-detail", kwargs={"slug": self.genre.slug})
#         self.jwt_login = reverse("user:jwt-login")

#         self.token = self.client.post(
#             self.jwt_login, data={"email": self.user1.email, "password": "Test,123"}
#         )
#         self.token1 = self.client.post(
#             self.jwt_login, data={"email": self.user2.email, "password": "Test,123"}
#         )

#     def test_get_genre_from_db_success(self):
#         cache.clear()

#         self.client.get(self.genre_detail)
#         # Checks that queries are cached properly
#         self.assertIsNotNone(cache.get(f"genre_{self.genre.slug}"))
#         cache.clear()

#         response = self.client.get(self.genre_detail)
#         self.assertIn("id", response.data)
#         self.assertIsInstance(response.data, dict)

#     def test_get_genre_from_cache_success(self):
#         cache.set(f"genre_{self.genre.slug}", self.genre)

#         response = self.client.get(self.genre_detail)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data["name"], self.genre.name)

#     def test_get_genre_failure(self):
#         url = reverse("palette:genre-detail", kwargs={"slug": "not-a-genre"})

#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
#         self.assertIn("Genre does not exist.", response.data)

#     def test_put_genre_success(self):
#         response = self.client.put(
#             self.genre_detail,
#             data={"name": "Cubism"},
#             headers={"Authorization": f"Bearer {self.token.data["access"]}"}
#         )
#         self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
#         self.assertEqual(response.data["slug"], "cubism")

#     def test_put_genre_failure(self):
#         response = self.client.put(
#             self.genre_detail,
#             data={"slug": "Cubism"},
#             headers={"Authorization": f"Bearer {self.token.data["access"]}"}
#         )
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(
#             "Update error. You can only update the Name field. Slug field updates automatically.",
#             response.data,
#         )
        
#         response1 = self.client.put(
#             self.genre_detail,
#             data={"slug": "Cubism"},
#             headers={"Authorization": f"Bearer {self.token1.data["access"]}"}
#         )
#         self.assertEqual(response1.status_code, status.HTTP_403_FORBIDDEN)
#         self.assertEqual(
#             "You must be an admin to perform this action.",
#             response1.data,
#         )
        
#         response3 = self.client.put(
#             self.genre_detail,
#             data={"slug": "Cubism"}
#         )
#         self.assertEqual(response3.status_code, status.HTTP_401_UNAUTHORIZED)
        
#         url = reverse("palette:genre-detail", kwargs={"slug": "not-a-genre"})
#         response = self.client.put(
#             url,
#             headers={"Authorization": f"Bearer {self.token.data["access"]}"}
#         )
#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
#         self.assertIn("Genre does not exist.", response.data)

#     def test_delete_genre_success(self):
#         response = self.client.delete(
#             self.genre_detail,
#             headers={"Authorization": f"Bearer {self.token.data["access"]}"}
#         )
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
#     def test_delete_genre_failure(self):
#         response = self.client.delete(
#             self.genre_detail,
#             headers={"Authorization": f"Bearer {self.token1.data["access"]}"}
#         )
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
#         self.assertEqual(
#             "You must be an admin to perform this action.",
#             response.data,
#         )
        
#         response1 = self.client.put(
#             self.genre_detail,
#             data={"slug": "Cubism"}
#         )
#         self.assertEqual(response1.status_code, status.HTTP_401_UNAUTHORIZED)
        
#     def tearDown(self):
#         super().tearDown()
#         sleep(15)


# class ArtworkListTestViewCase(APITestCase):
#     def setUp(self):
#         self.user1 = User.objects.create_user(
#             email="user1@gmail.com", username="user1", password="Test,123"
#         )
#         self.user2 = User.objects.create_user(
#             email="user3@gmail.com", username="user3", password="Test,123"
#         )
        
#         self.artist = Artist.objects.create(user=self.user1)
#         self.collector = Collector.objects.create(user=self.user2)
        
#         self.artwork_list = reverse("palette:artwork-list")
#         self.jwt_login = reverse("user:jwt-login")
#         self.genre = Genre.objects.create(name="Appropriation", slug="appropriation")

#         self.token = self.client.post(
#             self.jwt_login, data={"email": self.user1.email, "password": "Test,123"}
#         )
#         self.token1 = self.client.post(
#             self.jwt_login, data={"email": self.user2.email, "password": "Test,123"}
#         )

#     def test_get_artworks_from_db_success(self):
#         artwork = Artwork.objects.create(name="Mona Lisa", artist=self.artist)
#         artwork.genre.set([self.genre.id])
#         cache.clear()

#         self.client.get(self.artwork_list)
#         # Checks that queries are cached properly
#         self.assertIsNotNone(cache.get("artwork_list"))
#         cache.clear()

#         response = self.client.get(self.artwork_list)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 1)
#         self.assertEqual(response.data[0]["name"], artwork.name)
#         self.assertIsNotNone(cache.get("artwork_list"))

#     def test_get_artwork_from_cache_success(self):
#         artwork = Artwork.objects.create(name="Scream", artist=self.artist)
#         artwork.genre.set([self.genre.id])
#         cache.set("artwork_list", [artwork])

#         response = self.client.get(self.artwork_list)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 1)
#         self.assertEqual(response.data[0]["name"], artwork.name)

#     def test_create_artwork_success(self):
#         with open(image_file, "rb") as image:
#             data = {
#                 "name": "Mona Lisa",
#                 "genres": ["Appropriation"],
#                 "image": image
#             }
            
#             response = self.client.post(
#                 self.artwork_list,
#                 data,
#                 headers={"Authorization": f"Bearer {self.token.data["access"]}"}
#             )
#             self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#             self.assertEqual(Artwork.objects.count(), 1)
#             self.assertEqual(Artwork.objects.get().name, "Mona Lisa")
            
#             artwork = Artwork.objects.filter(id=response.data["id"])
#             artwork.delete()

#     def test_create_artwork_failure(self):
#         data = {"name": ""}

#         response = self.client.post(
#             self.artwork_list,
#             data,
#             headers={"Authorization": f"Bearer {self.token.data["access"]}"}
#         )
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(
#             [
#                 "Genres field is required.",
#                 "Name field cannot be blank.",
#                 "Image field is required."
#             ],
#             response.data,
#         )
        
#         response1 = self.client.post(self.artwork_list, data)
#         self.assertEqual(response1.status_code, status.HTTP_403_FORBIDDEN)
        
#         response2 = self.client.post(
#             self.artwork_list,
#             data,
#             headers={"Authorization": f"Bearer {self.token1.data["access"]}"}
#         )
#         self.assertEqual(response2.status_code, status.HTTP_403_FORBIDDEN)

#     def tearDown(self):
#         super().tearDown()
#         sleep(15)


# class ArtworkDetailViewTestCase(APITestCase):
#     def setUp(self):
#         self.user1 = User.objects.create_user(
#             email="user1@gmail.com", username="user1", password="Test,123"
#         )
#         self.user2 = User.objects.create_user(
#             email="user2@gmail.com", username="user2", password="Test,123"
#         )
#         self.user3 = User.objects.create_user(
#             email="user3@gmail.com", username="user3", password="Test,123"
#         )
            
#         self.artist1 = Artist.objects.create(user=self.user1)
#         self.artist2 = Artist.objects.create(user=self.user2)
#         self.collector = Collector.objects.create(user=self.user3)
        
#         self.genre = Genre.objects.create(name="Abstract", slug="abstract")
#         with open(image_file, "rb",) as image:
#             image_file_data = SimpleUploadedFile(
#                 "test.png", image.read(), content_type="image/png"
#             )
#             self.artwork = Artwork.objects.create(
#                 name="Abstracta",
#                 slug="abstracta",
#                 artist=self.artist1,
#                 image=image_file_data,
#             )
#             self.artwork.genre.set([self.genre.id])
            
#         self.artwork_detail = reverse("palette:artwork-detail", kwargs={"slug": self.artwork.slug})
#         self.jwt_login = reverse("user:jwt-login")
        
#         self.token1 = self.client.post(
#             self.jwt_login, data={"email": self.user1.email, "password": "Test,123"}
#         )
#         self.token2 = self.client.post(
#             self.jwt_login, data={"email": self.user2.email, "password": "Test,123"}
#         )
#         self.token3 = self.client.post(
#             self.jwt_login, data={"email": self.user3.email, "password": "Test,123"}
#         )
        
#     def test_get_artwork_from_db_success(self):
#         cache.clear()

#         self.client.get(self.artwork_detail)
#         # Checks that queries are cached properly
#         self.assertIsNotNone(cache.get(f"artwork_{self.artwork.slug}"))
#         cache.clear()

#         response = self.client.get(self.artwork_detail)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual("Abstracta", response.data["name"])

#     def test_get_artwork_from_cache_success(self):
#         cache.set(f"artwork_{self.artwork.slug}", self.artwork)

#         response = self.client.get(self.artwork_detail)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data["name"], self.artwork.name)

#     def test_get_artwork_failure(self):
#         url = reverse("palette:artwork-detail", kwargs={"slug": "not-an-artwork"})

#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
#         self.assertIn("Artwork does not exist.", response.data)

#     def test_put_artwork_success(self):
#         response = self.client.put(
#             self.artwork_detail,
#             data={"is_available": False},
#             headers={"Authorization": f"Bearer {self.token1.data["access"]}"}
#         )
#         self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
#         self.assertEqual(False, response.data["is_available"])
        
#     def test_put_artwork_failure(self):
#         response2 = self.client.put(
#             self.artwork_detail,
#             data={"name": "fake"},
#             headers={"Authorization": f"Bearer {self.token1.data["access"]}"}
#         )
#         self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(
#             "Update error. You cannot edit the value of ['name'].", response2.data
#         )

#         response3 = self.client.put(self.artwork_detail, data={"is_available": False})
#         self.assertEqual(response3.status_code, status.HTTP_403_FORBIDDEN)
#         self.assertEqual("You must be the artwork's creator to perform this action.", response3.data)
        
#         response4 = self.client.put(
#             self.artwork_detail,
#             data={"is_available": False},
#             headers={"Authorization": f"Bearer {self.token2.data["access"]}"}
#         )
#         self.assertEqual(response4.status_code, status.HTTP_403_FORBIDDEN)
#         self.assertEqual("You must be the artwork's creator to perform this action.", response4.data)  

#     def test_delete_artwork_success(self):
#         url2 = reverse("palette:artwork-list")
#         self.client.get(url2)
#         self.assertIsNotNone(cache.get("artwork_list"))
        
#         cache.set(f"artwork_{self.artwork.slug}", self.artwork)

#         self.client.get(self.artwork_detail)
#         self.assertIsNotNone(cache.get(f"artwork_{self.artwork.slug}"))

#         public_id = self.artwork.image.name
#         response = self.client.delete(
#             self.artwork_detail, 
#             headers={"Authorization": f"Bearer {self.token1.data["access"]}"}
#         )
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
#         self.assertEqual(0, len(cache.get("artwork_list")))
#         self.assertIsNone(cache.get(f"artwork_{self.artwork.slug}"))

#         result = None
#         try:
#             image = resource(public_id)
#             result = image
#         except Exception as e:
#             result = str(e)

#         self.assertIn("Resource not found", result)
        
#     def test_delete_artwork_failure(self):
#         response = self.client.delete(self.artwork_detail)
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
#         self.assertEqual("You must be the artwork's creator to perform this action.", response.data)
        
#         response2 = self.client.delete(
#             self.artwork_detail,
#             headers={"Authorization": f"Bearer {self.token2.data["access"]}"}
#         )
#         self.assertEqual(response2.status_code, status.HTTP_403_FORBIDDEN)
#         self.assertEqual(
#             "You must be the artwork's creator to perform this action.", response2.data
#         )
        
#         response3 = self.client.put(
#             self.artwork_detail,
#             data={"is_available": False},
#             headers={"Authorization": f"Bearer {self.token3.data["access"]}"}
#         )
#         self.assertEqual(response3.status_code, status.HTTP_403_FORBIDDEN)
#         self.assertEqual("You must be the artwork's creator to perform this action.", response3.data)
         
#     def tearDown(self):
#         super().tearDown()
#         sleep(15)


# class CartListTestCase(APITestCase):
#     def setUp(self):
#         self.cart_list = reverse("palette:cart-list")
#         self.jwt_login = reverse("user:jwt-login")
        
#         self.user1 = User.objects.create_user(
#             email="user1@gmail.com", username="user1", password="Test,123"
#         )
#         self.user2 = User.objects.create_user(
#             email="user2@gmail.com", username="user2", password="Test,123"
#         )
            
#         self.artist = Artist.objects.create(user=self.user1)
#         self.collector = Collector.objects.create(user=self.user2)
        
#         self.token1 = self.client.post(
#             self.jwt_login, data={"email": self.user1.email, "password": "Test,123"}
#         )
#         self.token2 = self.client.post(
#             self.jwt_login, data={"email": self.user2.email, "password": "Test,123"}
#         )

#     def test_get_cart_list_success(self):
#         response = self.client.get(
#             self.cart_list,
#             headers={"Authorization": f"Bearer {self.token2.data["access"]}"}
#         )
#         self.assertEqual({}, dict(response.data))
        
#     def test_get_cart_list_failure(self):
#         response = self.client.get(self.cart_list)
#         self.assertEqual("Authentication credentials were not provided.", response.data)
#         self.assertEqual(response.status_code, 401)
        
#         response1 = self.client.get(
#             self.cart_list,
#             headers={"Authorization": f"Bearer {self.token1.data["access"]}"}
#         )
#         self.assertEqual("You must be a collector to perform this action.", response1.data)
#         self.assertEqual(response1.status_code, 403)
        
#     def tearDown(self):
#         super().tearDown()
#         sleep(15)


class CartDetailTestCase(APITestCase):
    def setUp(self):
        self.jwt_login = reverse("user:jwt-login")
        
        self.user1 = User.objects.create_user(
            email="user1@gmail.com", username="user1", password="Test,123"
        )
        self.user2 = User.objects.create_user(
            email="user2@gmail.com", username="user2", password="Test,123"
        )
            
        self.artist = Artist.objects.create(user=self.user1)
        self.collector = Collector.objects.create(user=self.user2)
        
        self.genre = Genre.objects.create(name="Abstract", slug="abstract")
        with open(os.path.join(static_dir, "image/test.png"), "rb") as image:
            image_file = SimpleUploadedFile(
                "test.png", image.read(), content_type="image/png"
            )
            self.artwork = Artwork.objects.create(
                name="Abstracta",
                slug="abstracta",
                artist=self.artist,
                image=image_file,
            )
            self.artwork.genre.set([self.genre.id])
            
        self.cart_detail = reverse(
            "palette:cart-detail", kwargs={"artwork_id": self.artwork.id}
        )
        
        self.token1 = self.client.post(
            self.jwt_login, data={"email": self.user1.email, "password": "Test,123"}
        )
        self.token2 = self.client.post(
            self.jwt_login, data={"email": self.user2.email, "password": "Test,123"}
        )
        
    def test_post_cart_detail_success(self):
        response = self.client.post(
            self.cart_detail,
            headers={"Authorization": f"Bearer {self.token2.data["access"]}"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("artwork", list(response.data)[0])

        response1 = self.client.post(
            self.cart_detail,
            data={"quantity": 2},
            headers={"Authorization": f"Bearer {self.token2.data["access"]}"}
        )
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(3, list(response1.data)[0]["quantity"])
        
    def test_post_cart_detail_failure(self):
        response = self.client.post(
            reverse(
                "palette:cart-detail",
                kwargs={"artwork_id": "4d9dc378-24aa-4148-a8f7-772aad7915d7"},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual("Authentication credentials were not provided.", response.data)
        
        response1 = self.client.post(
            reverse(
                "palette:cart-detail",
                kwargs={"artwork_id": "4d9dc378-24aa-4148-a8f7-772aad7915d7"}
            ),
            headers={"Authorization": f"Bearer {self.token2.data["access"]}"}
        )
        self.assertEqual(response1.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual("Artwork not found.", response1.data)

    def test_put_cart_detail_success(self):
        response = self.client.put(
            self.cart_detail,
            headers={"Authorization": f"Bearer {self.token2.data["access"]}"}
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn("artwork", list(response.data)[0])

        response1 = self.client.put(
            self.cart_detail,
            data={"quantity": 2},
            headers={"Authorization": f"Bearer {self.token2.data["access"]}"}
        )
        self.assertEqual(response1.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(2, list(response1.data)[0]["quantity"])
        
    
    def test_put_cart_detail_failure(self):
        response = self.client.put(
            reverse(
                "palette:cart-detail",
                kwargs={"id": "4d9dc378-24aa-4148-a8f7-772aad7915d7"},
            ),
            headers={"Authorization": f"Bearer {self.token2.data["access"]}"}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual("Artwork not found.", response.data)
        
        response1 = self.client.put(
            reverse(
                "palette:cart-detail",
                kwargs={"artwork_id": "4d9dc378-24aa-4148-a8f7-772aad7915d7"},
            )
        )
        self.assertEqual(response1.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual("Authentication credentials were not provided.", response1.data)

    def test_delete_cart_detail_success(self):
        response = self.client.delete(
            self.cart_detail,
            headers={"Authorization": f"Bearer {self.token2.data["access"]}"}
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
    def test_delete_cart_detail_failure(self):
        response = self.client.delete(self.cart_detail)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual("Authentication credentials were not provided.", response.data)
        
    def tearDown(self):
        artwork = Artwork.objects.filter(id=self.artwork.id)
        artwork.delete()
        super().tearDown()
        sleep(15)
