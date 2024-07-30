from django.db.transaction import atomic
from django.core.cache import cache

from .serializers import (
    GenreSerializer,
    ArtworkSerializer,
    Genre,
    Artwork,
    CartUpdateSerializer,
)
from .cart import Cart
from portal.permissions import (IsAdminOrReadOnly, IsArtistOrReadOnly, IsCreatorOrReadOnly, IsCollectorOrReadOnly)
from user.views import JWTAuthentication, PaletteTokenAuthentication
from .tasks import update_palette_cache_details

from rest_framework.views import APIView
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import CursorPagination
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from uuid import UUID
import pickle
from drf_spectacular.utils import extend_schema


class PalettePagination(CursorPagination):
    page_size = 15
    ordering = "-created"


class GenreListView(APIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = GenreSerializer
    authentication_classes = [JWTAuthentication, PaletteTokenAuthentication]
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = PalettePagination

    @extend_schema(
        operation_id="v1_genre_list_retrieve",
        tags=["genre_v1"],
    )
    def get(self, request):
        """
        Retrieves an existing cached list of all existing genres.
        If none exists, retrieves an caches a non-cached list.
        """
        cached_genres = cache.get("genre_list")
        if cached_genres is not None:
            genres = pickle.loads(cached_genres)
        else:
            genres = Genre.objects.all()
            cache.set("genre_list", pickle.dumps(genres))
            
        paginator = self.pagination_class()
        paginated_genres = paginator.paginate_queryset(genres, request, view=self)
        genre_data = self.serializer_class(paginated_genres, many=True).data
        return paginator.get_paginated_response(genre_data)

    @extend_schema(
        operation_id="v1_genre_create",
        tags=["genre_v1"],
    )
    def post(self, request):
        # Creates a new genre object
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            with atomic():
                genre = serializer.save()

            genre_data = self.serializer_class(genre).data
            return Response(genre_data, status=status.HTTP_201_CREATED)


class GenreDetailView(APIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = GenreSerializer
    authentication_classes = [JWTAuthentication, PaletteTokenAuthentication]
    permission_classes = [IsAdminOrReadOnly]

    @extend_schema(
        operation_id="v1_genre_retrieve",
        tags=["genre_v1"],
    )
    def get(self, request, slug):
        """
        Retrieves an existing cached genre object.
        If none exists, retrieves an caches an non-cached object.
        """
        cached_genre = cache.get(f"genre_{slug}")
        if cached_genre is not None:
            genre = pickle.loads(cached_genre)
        else:
            genre = Genre.objects.filter(slug=slug).first()
            if genre:
                update_palette_cache_details.delay(slug, "genre")
            else:
                return Response("Genre does not exist.", status=status.HTTP_404_NOT_FOUND)

        data = self.serializer_class(genre).data
        return Response(data, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="v1_genre_update",
        tags=["genre_v1"],
    )
    def put(self, request, slug):
        """
        Updates an existing genre object.
        Also updates the cache for both genre list and corresponding genre object.
        """
        cached_genre = cache.get(f"genre_{slug}")
        if cached_genre is not None:
            genre = pickle.loads(cached_genre)
        else:
            genre = Genre.objects.filter(slug=slug).first()
            if not genre:
                return Response("Genre does not exist.", status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(genre, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            with atomic():
                genre = serializer.save()
                
            genre_data = self.serializer_class(genre).data
            update_palette_cache_details.delay(genre_data["slug"], "genre")
            return Response(genre_data, status=status.HTTP_202_ACCEPTED)

    @extend_schema(
        operation_id="v1_genre_delete",
        tags=["genre_v1"],
    )
    def delete(self, request, slug):
        """
        Deletes an existing genre object.
        Also deletes the cache for corresponding genre object, and updates that of genre list.
        """
        cached_genre = cache.get(f"genre_{slug}")
        if cached_genre is not None:
            genre = pickle.loads(cached_genre)
        else:
            genre = Genre.objects.filter(slug=slug).first()
            if not genre:
                return Response("Genre does not exist.", status=status.HTTP_404_NOT_FOUND)

        with atomic():
            genre.delete()

        update_palette_cache_details.delay(slug, "genre", is_delete=True)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ArtworkListView(APIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    parser_classes = [MultiPartParser]
    serializer_class = ArtworkSerializer
    authentication_classes = [JWTAuthentication, PaletteTokenAuthentication]
    permission_classes = [IsArtistOrReadOnly]
    pagination_class = PalettePagination

    @extend_schema(
        operation_id="v1_artwork_list_retrieve",
        tags=["artwork_v1"],
    )
    def get(self, request):
        """
        Retrieves an existing cached list of all existing artworks.
        If none exists, retrieves an caches a non-cached list.
        """
        cached_artworks = cache.get("artwork_list")
        if cached_artworks is not None:
            artworks = pickle.loads(cached_artworks)
        else:
            artworks = Artwork.objects.all()
            cache.set("artwork_list", pickle.dumps(artworks))
            
        paginator = self.pagination_class()
        paginated_artworks = paginator.paginate_queryset(artworks, request, view=self)
        artwork_data = self.serializer_class(paginated_artworks, many=True).data
        return paginator.get_paginated_response(artwork_data)

    @extend_schema(
        operation_id="v1_artwork_create",
        tags=["artwork_v1"],
    )
    def post(self, request):
        # Creates a new artwork object using form-data (multi-part content)
        serializer = self.serializer_class(
            data=request.data, context={"data": request.data, "user": request.user}
        )
        if serializer.is_valid(raise_exception=True):
            with atomic():
                artwork = serializer.save()

            artwork_data = self.serializer_class(artwork).data
            return Response(artwork_data, status=status.HTTP_201_CREATED)


class ArtworkDetailView(APIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    parser_classes = [MultiPartParser]
    serializer_class = ArtworkSerializer
    authentication_classes = [JWTAuthentication, PaletteTokenAuthentication]
    permission_classes = [IsCreatorOrReadOnly]

    @extend_schema(
        operation_id="v1_artwork_retrieve",
        tags=["artwork_v1"],
    )
    def get(self, request, slug):
        """
        Retrieves an existing cached artwork object.
        If none exists, retrieves an caches an non-cached object.
        """
        cached_artwork = cache.get(f"artwork_{slug}")
        if cached_artwork is not None:
            artwork = pickle.loads(cached_artwork)
        else:
            artwork = Artwork.objects.filter(slug=slug).first()
            if artwork:
                update_palette_cache_details.delay(slug, "artwork")
            else:
                return Response("Artwork does not exist.", status=status.HTTP_404_NOT_FOUND)

        data = self.serializer_class(artwork).data
        return Response(data, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="v1_artwork_update",
        tags=["artwork_v1"],
    )
    def put(self, request, slug):
        """
        Updates an existing artwork object.
        Also updates the cache for both artwork list and corresponding artwork object.
        """
        cached_artwork = cache.get(f"artwork_{slug}")
        if cached_artwork is not None:
            artwork = pickle.loads(cached_artwork)
        else:
            artwork = Artwork.objects.filter(slug=slug).first()
            if not artwork:
                return Response("Artwork does not exist.", status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(artwork, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            with atomic():
                artwork = serializer.save()

            artwork_data = self.serializer_class(artwork).data
            update_palette_cache_details.delay(artwork_data["slug"], "artwork")
            return Response(artwork_data, status=status.HTTP_202_ACCEPTED)

    @extend_schema(
        operation_id="v1_artwork_delete",
        tags=["artwork_v1"],
    )
    def delete(self, request, slug):
        """
        Deletes an existing artwork object.
        Also deletes the cache for corresponding artwork object, and updates that of artwork list.
        """
        cached_artwork = cache.get(f"artwork_{slug}")
        if cached_artwork is not None:
            artwork = pickle.loads(cached_artwork)
        else:
            artwork = Artwork.objects.filter(slug=slug).first()
            if not artwork:
                return Response("Artwork does not exist.", status=status.HTTP_404_NOT_FOUND)
            
        with atomic():
            artwork.delete()
            
        update_palette_cache_details.delay(slug, "artwork", is_delete=True)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartListView(APIView):
    throttle_classes = [AnonRateThrottle]
    authentication_classes = [JWTAuthentication, PaletteTokenAuthentication]
    permission_classes = [IsAuthenticated, IsCollectorOrReadOnly]

    @extend_schema(
        operation_id="v1_cart_retrieve",
        tags=["cart_v1"],
    )
    def get(self, request):
        """
        Retrieves a dict of all existing cart items.
        """
        cart = Cart(request)
        return Response(cart, status=status.HTTP_200_OK)


class CartDetailView(APIView):
    throttle_classes = [AnonRateThrottle]
    serializer_class = CartUpdateSerializer
    authentication_classes = [JWTAuthentication, PaletteTokenAuthentication]
    permission_classes = [IsAuthenticated, IsCollectorOrReadOnly]

    @extend_schema(
        operation_id="v1_cart_create",
        tags=["cart_v1"],
    )
    def post(self, request, artwork_id):
        # Increments the quantity of artwork items in cart
        cached_artwork = cache.get(f"artwork_{artwork_id}")
        if cached_artwork is not None:
            artwork = pickle.loads(cached_artwork)
        else:
            artwork = Artwork.available.filter(id=artwork_id).first()
            if not artwork:
                return Response("Artwork does not exist.", status=status.HTTP_404_NOT_FOUND)
            update_palette_cache_details.delay(artwork.slug, "artwork", object_id=artwork.id)

        serializer = self.serializer_class(
            data=request.data, context={"request": request, "artwork": artwork}
        )
        if serializer.is_valid(raise_exception=True):
            cart_data = serializer.save()
            return Response(cart_data, status=status.HTTP_201_CREATED)

    @extend_schema(
        operation_id="v1_cart_update",
        tags=["cart_v1"],
    )
    def put(self, request, artwork_id):
        # Sets the quantity of artwork items in cart to a specific value
        cached_artwork = cache.get(f"artwork_{artwork_id}")
        if cached_artwork is not None:
            artwork = pickle.loads(cached_artwork)
        else:
            artwork = Artwork.available.filter(id=artwork_id).first()
            if not artwork:
                return Response("Artwork does not exist.", status=status.HTTP_404_NOT_FOUND)
            update_palette_cache_details.delay(artwork.slug, "artwork", object_id=artwork.id)

        serializer = self.serializer_class(
            artwork, data=request.data, context={"request": request}
        )
        if serializer.is_valid(raise_exception=True):
            cart_list = serializer.save()
            return Response(cart_list, status=status.HTTP_202_ACCEPTED)

    @extend_schema(
        operation_id="v1_cart_delete",
        tags=["cart_v1"],
    )
    def delete(self, request, artwork_id):
        # Removes artwork items from cart
        cart = Cart(request)
        cached_artwork = cache.get(f"artwork_{artwork_id}")
        if cached_artwork is not None:
            artwork = pickle.loads(cached_artwork)
        else:
            artwork = Artwork.available.filter(id=artwork_id).first()
            if not artwork:
                return Response("Artwork does not exist.", status=status.HTTP_404_NOT_FOUND)
            update_palette_cache_details.delay(artwork.slug, "artwork", object_id=artwork.id)

        cart.remove(artwork)
        return Response(status=status.HTTP_204_NO_CONTENT)
