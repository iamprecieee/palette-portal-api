from django.db.transaction import atomic
from django.contrib.auth.signals import user_logged_out
from django.core.cache import cache

from .serializers import (
    User,
    RegisterSerializer,
    LoginSerializer,
    RefreshTokenSerializer,
    Artist,
    Collector,
    ArtistProfileSerializer,
    CollectorProfileSerializer,
)
from .models import PaletteTokenAuthentication, JWTTokenBlacklist
from .refresh import SessionRefreshToken
from portal.permissions import IsCurrentOwnerOrReadOnly

from rest_framework.views import APIView
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from knox.views import LoginView, LogoutAllView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication
from uuid import UUID


class RegisterView(APIView):
    throttle_classes = [AnonRateThrottle]
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            with atomic():
                user = serializer.save()

            user_data = self.serializer_class(user).data

            return Response(user_data, status=status.HTTP_201_CREATED)


class KnoxLoginView(LoginView):
    throttle_classes = [AnonRateThrottle]
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid(raise_exception=True):
            user, token = serializer.authenticate_user()
            user_data = self.serializer_class(user).data
            user_data["token"] = token

            return Response(user_data, status=status.HTTP_200_OK)


class JWTLoginView(TokenObtainPairView):
    throttle_classes = [AnonRateThrottle]
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            login_data = serializer.validated_data
            user = User.objects.filter(email=request.data["email"]).first()
            login_data["id"] = str(user.id)
            login_data["email"] = user.email
            login_data["username"] = user.username

            refresh = SessionRefreshToken(request)
            refresh.remove()
            refresh.add(login_data["refresh"])

            return Response(login_data, status=status.HTTP_200_OK)


class JWTRefreshView(APIView):
    throttle_classes = [AnonRateThrottle]
    permission_classes = [AllowAny]
    serializer_class = RefreshTokenSerializer

    def post(self, request):
        refresh = SessionRefreshToken(request)
        serializer = self.serializer_class(
            context={"request": request, "refresh": refresh.token()}
        )
        access_data = serializer.validate()
        data = self.serializer_class(access_data).data

        return Response(data, status=status.HTTP_200_OK)


class MockLoginView(APIView):
    throttle_classes = [UserRateThrottle]
    authentication_classes = [PaletteTokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response("Hello world.", status=status.HTTP_200_OK)


class KnoxLogoutView(APIView):
    throttle_classes = [UserRateThrottle]
    authentication_classes = [PaletteTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request._auth.delete()
        user_logged_out.send(
            sender=request.user.__class__, request=request, user=request.user
        )

        return Response("User logged out successfully.", status=status.HTTP_200_OK)


class JWTLogoutView(APIView):
    throttle_classes = [UserRateThrottle]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @staticmethod
    def blacklist_token(token, user):
        JWTTokenBlacklist.objects.create(token=token, user=user)

    def post(self, request):
        refresh = SessionRefreshToken(request)
        auth_header = request.headers["Authorization"]
        if "Bearer" in auth_header:
            access_token = auth_header.split(" ")[1]
            blacklist = JWTTokenBlacklist.objects.filter(user=request.user)
            with atomic():
                if blacklist.count() == 3:
                    blacklist.last().delete()

                self.blacklist_token(access_token, request.user)
                refresh.remove()

        return Response("User logged out successfully.", status=status.HTTP_200_OK)


class KnoxLogoutAllView(LogoutAllView):
    throttle_classes = [UserRateThrottle]
    authentication_classes = [PaletteTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.palette_auth_token_set.all().delete()
        user_logged_out.send(
            sender=request.user.__class__, request=request, user=request.user
        )

        return Response("Batch logout successful.", status=status.HTTP_200_OK)


class ArtistProfileListView(APIView):
    throttle_classes = [UserRateThrottle]
    authentication_classes = [PaletteTokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ArtistProfileSerializer

    def get(self, request):
        artists = cache.get("artist_list")
        if not artists or len(artists) == 0:
            artists = Artist.objects.all()
            cache.set("artist_list", artists)
            
        artist_data = self.serializer_class(artists, many=True).data
        
        return Response(artist_data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={"user": request.user}
        )
        if serializer.is_valid(raise_exception=True):
            with atomic():
                new_profile = serializer.save()

            artist_data = self.serializer_class(new_profile).data
            
            return Response(artist_data, status=status.HTTP_201_CREATED)


class ArtistProfileDetailView(APIView):
    throttle_classes = [UserRateThrottle]
    authentication_classes = [PaletteTokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated, IsCurrentOwnerOrReadOnly]
    serializer_class = ArtistProfileSerializer

    def get(self, request, profile_id):
        artist = Artist.objects.filter(id=profile_id).first()
        artist_data = self.serializer_class(artist).data

        return Response(artist_data, status=status.HTTP_200_OK)

    def put(self, request, profile_id):
        artist = Artist.objects.filter(id=profile_id).first()
        serializer = self.serializer_class(
            artist,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid(raise_exception=True):
            with atomic():
                profile_data = serializer.save()
                artists_cache = cache.get("artist_list", [])
                artists_cache = [i for i in artists_cache if i.id != profile_id]
                artists_cache.append(artist)
                cache.set("artist_list", artists_cache)
                
            artist_data = self.serializer_class(profile_data).data
            return Response(artist_data, status=status.HTTP_202_ACCEPTED)

    def delete(self, request, profile_id):
        artist = Artist.objects.filter(id=profile_id).first()
        with atomic():
            artists_cache = cache.get("artist_list", [])
            artists_cache = [i for i in artists_cache if i.id != profile_id]
            cache.set("artist_list", artists_cache)
            artist.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class CollectorProfileListView(APIView):
    throttle_classes = [UserRateThrottle]
    authentication_classes = [PaletteTokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CollectorProfileSerializer

    def get(self, request):
        collectors = cache.get("collector_list")
        if not collectors  or len(collectors) == 0:
            collectors = Collector.objects.all()
            cache.set("collector_list", collectors)
            
        collectors_data = self.serializer_class(collectors, many=True).data
        
        return Response(collectors_data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={"user": request.user}
        )
        if serializer.is_valid(raise_exception=True):
            with atomic():
                new_profile = serializer.save()

            collector_data = self.serializer_class(new_profile).data

            return Response(collector_data, status=status.HTTP_201_CREATED)


class CollectorProfileDetailView(APIView):
    throttle_classes = [UserRateThrottle]
    authentication_classes = [PaletteTokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated, IsCurrentOwnerOrReadOnly]
    serializer_class = CollectorProfileSerializer

    def get(self, request, profile_id):
        collector = Collector.objects.filter(id=profile_id).first()
        collector_data = self.serializer_class(collector).data

        return Response(collector_data, status=status.HTTP_200_OK)

    def put(self, request, profile_id):
        collector = Collector.objects.filter(id=profile_id).first()
        serializer = self.serializer_class(
            collector,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid(raise_exception=True):
            with atomic():
                profile_data = serializer.save()
                collectors_cache = cache.get("collector_list", [])
                collectors_cache = [i for i in collectors_cache if i.id != profile_id]
                collectors_cache.append(collector)
                cache.set("collector_list", collectors_cache)
                
            collector_data = self.serializer_class(profile_data).data
            return Response(collector_data, status=status.HTTP_202_ACCEPTED)

    def delete(self, request, profile_id):
        collector = Collector.objects.filter(id=profile_id).first()
        with atomic():
            collectors_cache = cache.get("collector_list", [])
            collectors_cache = [i for i in collectors_cache if i.id != profile_id]
            cache.set("collector_list", collectors_cache)
            collector.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class CronJobAction(APIView):
    def get(self, request):
        return Response("Success", status=status.HTTP_200_OK)
