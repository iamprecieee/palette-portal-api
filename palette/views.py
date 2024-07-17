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

from rest_framework.views import APIView
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from uuid import UUID


class GenreListView(APIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = GenreSerializer
    authentication_classes = [JWTAuthentication, PaletteTokenAuthentication]
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        """
        Retrieves an existing cached list of all existing genres.
        If none exists, retrieves an caches a non-cached list.
        """
        genres = cache.get("genre_list")
        if not genres or len(genres) == 0:
            genres = Genre.objects.all()
            cache.set("genre_list", genres)

        data = self.serializer_class(genres, many=True).data
        return Response(data, status=status.HTTP_200_OK)

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

    def get(self, request, slug):
        """
        Retrieves an existing cached genre object.
        If none exists, retrieves an caches an non-cached object.
        """
        genre = cache.get(f"genre_{slug}")
        if not genre:
            genre = Genre.objects.filter(slug=slug).first()
            if genre:
                cache.set(f"genre_{slug}", genre)

        if not genre:
            return Response("Genre does not exist.", status=status.HTTP_404_NOT_FOUND)

        data = self.serializer_class(genre).data
        return Response(data, status=status.HTTP_200_OK)

    def put(self, request, slug):
        """
        Updates an existing genre object.
        Also updates the cache for both genre list and corresponding genre object.
        """
        genre = cache.get(f"genre_{slug}")
        if not genre:
            genre = Genre.objects.filter(slug=slug).first()
        
        if not genre:
            return Response("Genre does not exist.", status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(genre, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            with atomic():
                genre = serializer.save()
                cache.set(f"genre_{slug}", genre)
                genres_cache = cache.get("genre_list", [])
                genres_cache = [i for i in genres_cache if i.slug != slug]
                genres_cache.append(genre)
                cache.set("genre_list", genres_cache)

            genre_data = self.serializer_class(genre).data
            return Response(genre_data, status=status.HTTP_202_ACCEPTED)

    def delete(self, request, slug):
        """
        Deletes an existing genre object.
        Also deletes the cache for corresponding genre object, and updates that of genre list.
        """
        genre = cache.get(f"genre_{slug}")
        if not genre:
            genre = Genre.objects.filter(slug=slug).first()
            
        if not genre:
            return Response("Genre does not exist.", status=status.HTTP_404_NOT_FOUND)

        with atomic():
            cache.delete(f"genre_{slug}")
            genres_cache = cache.get("genre_list", [])
            genres_cache = [i for i in genres_cache if i.slug != slug]
            cache.set("genre_list", genres_cache)
            genre.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ArtworkListView(APIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    parser_classes = [MultiPartParser]
    serializer_class = ArtworkSerializer
    authentication_classes = [JWTAuthentication, PaletteTokenAuthentication]
    permission_classes = [IsArtistOrReadOnly]

    def get(self, request):
        """
        Retrieves an existing cached list of all existing artworks.
        If none exists, retrieves an caches a non-cached list.
        """
        artworks = cache.get("artwork_list")
        if not artworks or len(artworks) == 0:
            artworks = Artwork.available.all()
            cache.set("artwork_list", artworks)

        data = self.serializer_class(artworks, many=True).data
        return Response(data, status=status.HTTP_200_OK)

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

    def get(self, request, slug):
        """
        Retrieves an existing cached artwork object.
        If none exists, retrieves an caches an non-cached object.
        """
        artwork = cache.get(f"artwork_{slug}")
        if not artwork:
            artwork = Artwork.available.filter(slug=slug).first()
            if artwork:
                cache.set(f"artwork_{slug}", artwork)

        if not artwork:
            return Response("Artwork not found.", status=status.HTTP_404_NOT_FOUND)

        data = self.serializer_class(artwork).data
        return Response(data, status=status.HTTP_200_OK)

    def put(self, request, slug):
        """
        Updates an existing artwork object.
        Also updates the cache for both artwork list and corresponding artwork object.
        """
        artwork = Artwork.objects.filter(slug=slug).first()
        serializer = self.serializer_class(artwork, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            with atomic():
                artwork = serializer.save()
                cache.set(f"artwork_{slug}", artwork)
                artworks_cache = cache.get("artwork_list", [])
                artworks_cache = [i for i in artworks_cache if i.slug != slug]
                artworks_cache.append(artwork)
                cache.set("artwork_list", artworks_cache)

            artwork_data = self.serializer_class(artwork).data
            return Response(artwork_data, status=status.HTTP_202_ACCEPTED)

    def delete(self, request, slug):
        """
        Deletes an existing artwork object.
        Also deletes the cache for corresponding artwork object, and updates that of artwork list.
        """
        artwork = Artwork.objects.filter(slug=slug).first()
        with atomic():
            cache.delete(f"artwork_{slug}")
            artworks_cache = cache.get("artwork_list", [])
            artworks_cache = [i for i in artworks_cache if i.slug != slug]
            cache.set("artwork_list", artworks_cache)
            artwork.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class CartListView(APIView):
    throttle_classes = [AnonRateThrottle]
    authentication_classes = [JWTAuthentication, PaletteTokenAuthentication]
    permission_classes = [IsAuthenticated, IsCollectorOrReadOnly]

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

    def post(self, request, artwork_id):
        # Increments the quantity of artwork items in cart
        artwork = Artwork.available.filter(id=artwork_id).first()
        if not artwork:
            return Response("Artwork not found.", status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(
            data=request.data, context={"request": request, "artwork": artwork}
        )
        if serializer.is_valid(raise_exception=True):
            cart_data = serializer.save()
            return Response(cart_data, status=status.HTTP_201_CREATED)

    def put(self, request, id):
        # Sets the quantity of artwork items in cart to a specific value
        artwork = Artwork.available.filter(id=id).first()
        if not artwork:
            return Response("Artwork not found.", status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(
            artwork, data=request.data, context={"request": request}
        )
        if serializer.is_valid(raise_exception=True):
            cart_list = serializer.save()
            return Response(cart_list, status=status.HTTP_202_ACCEPTED)

    def delete(self, request, artwork_id):
        UUID(artwork_id)

        # Removes artwork items from cart
        cart = Cart(request)
        artwork = Artwork.available.filter(id=artwork_id).first()
        if not artwork:
            return Response("Artwork not found.", status=status.HTTP_404_NOT_FOUND)

        cart.remove(artwork)
        return Response(status=status.HTTP_204_NO_CONTENT)
