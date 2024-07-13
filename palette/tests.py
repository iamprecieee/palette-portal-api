from django.urls import reverse
from django.core.cache import cache
import os
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from .models import Genre, Artwork
from .cart import Cart

from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework import status
from cloudinary.api import resource


static_dir = settings.STATICFILES_DIRS[0]


class GenreListTestCase(APITestCase):
    def setUp(self):
        self.url = reverse("palette:genre-list")

    def test_get_genres_from_db(self):
        genre = Genre.objects.create(name="Abstract")
        cache.clear()

        self.client.get(self.url)

        # Checks that queries are cached properly
        self.assertIsNotNone(cache.get("genre_list"))
        cache.clear()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], genre.name)
        self.assertIsNotNone(cache.get("genre_list"))

    def test_get_genres_from_cache(self):
        genre = Genre.objects.create(name="Vector")
        cache.set("genre_list", [genre])

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], genre.name)

    def test_create_genre_success(self):
        data = {"name": "Cubism"}

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Genre.objects.count(), 1)
        self.assertEqual(Genre.objects.get().name, "Cubism")

    def test_create_genre_failure(self):
        data = {"name": ""}

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual("Name field cannot be blank.", response.data)

    def test_throttling(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for i in range(0, 10):
            response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertIn("Request was throttled", response.data)


class GenreDetailTestCase(APITestCase):
    def setUp(self):
        self.genre = Genre.objects.create(name="Abstract", slug="abstract")
        self.url = reverse("palette:genre-detail", kwargs={"slug": self.genre.slug})

    def test_get_genre_from_db(self):
        cache.clear()

        self.client.get(self.url)

        # Checks that queries are cached properly
        self.assertIsNotNone(cache.get(f"genre_{self.genre.slug}"))
        cache.clear()

        response = self.client.get(self.url)
        self.assertIn("id", response.data)
        self.assertIsInstance(response.data, dict)

    def test_get_genre_from_cache(self):
        cache.set(f"genre_{self.genre.slug}", self.genre)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.genre.name)

    def test_get_genre_not_found(self):
        url = reverse("palette:genre-detail", kwargs={"slug": "not-a-genre"})

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("Genre not found.", response.data)

    def test_put_genre_success(self):
        response = self.client.put(self.url, data={"name": "Cubism"})

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data["slug"], "cubism")

    def test_put_genre_slug_not_name(self):
        response = self.client.put(self.url, data={"slug": "Cubism"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            "Update error. You can only update the Name field. Slug field updates automatically.",
            response.data,
        )

    def test_delete_genre(self):
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class ArtworkListTestCase(APITestCase):
    def setUp(self):
        self.url = reverse("palette:artwork-list")
        self.genre = Genre.objects.create(name="Appropriation", slug="appropriation")

    def test_get_artworks_from_db(self):
        artwork = Artwork.objects.create(name="Mona Lisa")
        artwork.genre.set([self.genre.id])
        cache.clear()

        self.client.get(self.url)

        # Checks that queries are cached properly
        self.assertIsNotNone(cache.get("artwork_list"))
        cache.clear()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], artwork.name)
        self.assertIsNotNone(cache.get("artwork_list"))

    def test_get_artwork_from_cache(self):
        artwork = Artwork.objects.create(name="Scream")
        artwork.genre.set([self.genre.id])
        cache.set("artwork_list", [artwork])

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], artwork.name)

    def test_create_artwork_success(self):
        with open(
            os.path.join(os.path.dirname(__file__), "test-image/test.png"), "rb"
        ) as image:
            data = {
                "name": "Mona Lisa",
                "genres": ["Appropriation"],
                "artist": "iamprecieee",
                "image": image,
            }

            response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Artwork.objects.count(), 1)
        self.assertEqual(Artwork.objects.get().name, "Mona Lisa")

    def test_create_artwork_failure(self):
        data = {"name": ""}

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            [
                "Genres field is required.",
                "Name field cannot be blank.",
                "Image field is required.",
                "Artist field is required.",
            ],
            response.data,
        )


class ArtworkDetailTestCase(APITestCase):
    def setUp(self):
        self.genre = Genre.objects.create(name="Abstract", slug="abstract")
        with open(
            # os.path.join(os.path.dirname(__file__), "test-image/test.png"), "rb"
            os.path.join(static_dir, "image/test.png"),
            "rb",
        ) as image:
            image_file = SimpleUploadedFile(
                "test.png", image.read(), content_type="image/png"
            )
            self.artwork = Artwork.objects.create(
                name="Abstracta",
                slug="abstracta",
                artist="iamprecieee",
                image=image_file,
            )
            self.artwork.genre.set([self.genre.id])
        self.url = reverse("palette:artwork-detail", kwargs={"slug": self.artwork.slug})

    def test_get_artwork_from_db(self):
        cache.clear()

        self.client.get(self.url)

        # Checks that queries are cached properly
        self.assertIsNotNone(cache.get(f"artwork_{self.artwork.slug}"))
        cache.clear()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual("Abstracta", response.data["name"])

    def test_get_artwork_from_cache(self):
        cache.set(f"artwork_{self.artwork.slug}", self.artwork)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.artwork.name)

    def test_get_artwork_not_found(self):
        url = reverse("palette:artwork-detail", kwargs={"slug": "not-an-artwork"})

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("Artwork not found.", response.data)

    def test_put_artwork(self):
        response = self.client.put(
            self.url, data={"name": "fake", "artist": "michelangelo"}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            "Update error. You cannot edit the values of name, artist.", response.data
        )

        response2 = self.client.put(self.url, data={"is_available": False})

        self.assertEqual(response2.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(False, response2.data["is_available"])

    def test_delete_artwork(self):
        url2 = reverse("palette:artwork-list")
        self.client.get(url2)
        self.assertIsNotNone(cache.get("artwork_list"))

        self.client.get(self.url)
        self.assertIsNotNone(cache.get(f"artwork_{self.artwork.slug}"))

        public_id = self.artwork.image.name
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(0, len(cache.get("artwork_list")))
        self.assertIsNone(cache.get(f"artwork_{self.artwork.slug}"))

        result = None
        try:
            image = resource(public_id)
            result = image
        except Exception as e:
            result = str(e)

        self.assertIn("Resource not found", result)


class CartListTestCase(APITestCase):
    def setUp(self):
        self.url = reverse("palette:cart-list")

    def test_get_cart_list(self):
        response = self.client.get(self.url)
        self.assertEqual({}, dict(response.data))


class CartDetailTestCase(APITestCase):
    def setUp(self):
        self.genre = Genre.objects.create(name="Abstract", slug="abstract")
        with open(os.path.join(static_dir, "image/test.png"), "rb") as image:
            image_file = SimpleUploadedFile(
                "test.png", image.read(), content_type="image/png"
            )
            self.artwork = Artwork.objects.create(
                name="Abstracta",
                slug="abstracta",
                artist="iamprecieee",
                image=image_file,
            )
            self.artwork.genre.set([self.genre.id])

        self.url = reverse(
            "palette:cart-detail", kwargs={"artwork_id": self.artwork.id}
        )

    def test_post_cart_detail(self):
        response = self.client.post(
            reverse(
                "palette:cart-detail",
                kwargs={"id": "4d9dc378-24aa-4148-a8f7-772aad7915d7"},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual("Artwork not found.", response.data)

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("artwork", list(response.data)[0])

        response = self.client.post(self.url, data={"quantity": 2})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(3, list(response.data)[0]["quantity"])

    def test_put_cart_detail(self):
        response = self.client.put(
            reverse(
                "palette:cart-detail",
                kwargs={"id": "4d9dc378-24aa-4148-a8f7-772aad7915d7"},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual("Artwork not found.", response.data)

        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn("artwork", list(response.data)[0])

        response = self.client.put(self.url, data={"quantity": 2})
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(2, list(response.data)[0]["quantity"])

    def test_delete_cart_detail(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
