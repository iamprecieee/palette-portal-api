from django.db.transaction import atomic
from django.contrib.auth.signals import user_logged_out
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator

from .serializers import (
    User,
    RegisterSerializer,
    KnoxLoginSerializer,
    RefreshTokenSerializer,
    Artist,
    Collector,
    ArtistProfileSerializer,
    CollectorProfileSerializer,
    EmailVerificationOTPSerializer,
    RequestEmailVerificationSerializer,
    PasswordChangeSerializer,
)
from .models import PaletteTokenAuthentication
from .refresh import SessionRefreshToken
from portal.permissions import IsCurrentOwnerOrReadOnly
from .tasks import store_access_token, delete_access_token, update_cache_details, send_otp
from .social_authentication import begin_social_authentication, complete_social_authentication

from rest_framework.views import APIView
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import CursorPagination
from knox.views import LoginView, LogoutAllView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication
from uuid import UUID
import pickle
from social_django.utils import psa
from drf_spectacular.utils import extend_schema


class UserPagination(CursorPagination):
    page_size = 15
    ordering = "-created"


class RegisterView(APIView):
    throttle_classes = [AnonRateThrottle]
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    @extend_schema(
        operation_id="v1_register",
        tags=["auth_v1"],
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            with atomic():
                user = serializer.save()

            user_data = self.serializer_class(user).data
            send_otp.delay(user_data["email"])
            return Response(f"""
                            {user_data},
                            A verification OTP has been sent to your email address.
                            """,
                            status=status.HTTP_201_CREATED)
        
        
class VerifyUserEmailBeginView(APIView):
    throttle_classes = [AnonRateThrottle]
    permission_classes = [AllowAny]
    serializer_class = RequestEmailVerificationSerializer
    
    @extend_schema(
        operation_id="v1_verify_email_begin",
        tags=["auth_v1"],
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response("A verification OTP has been sent to your email address.", status=status.HTTP_200_OK)
    
        
class VerifyUserEmailCompleteView(APIView):
    throttle_classes = [AnonRateThrottle]
    permission_classes = [AllowAny]
    serializer_class = EmailVerificationOTPSerializer
    
    @extend_schema(
        operation_id="v1_verify_email_complete",
        tags=["auth_v1"],
    )
    def post(self, request, token):
        serializer = self.serializer_class(data={"token": token})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response("Email verified successfully.", status=status.HTTP_200_OK)
        

class ChangePasswordBeginView(APIView):
    throttle_classes = [AnonRateThrottle]
    permission_classes = [AllowAny]
    serializer_class = PasswordChangeSerializer
    
    @extend_schema(
        operation_id="v1_change_password_begin",
        tags=["auth_v1"],
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response("A password change link has been sent to your email address.", status=status.HTTP_200_OK)
    
        
class ChangePasswordCompleteView(APIView):
    throttle_classes = [AnonRateThrottle]
    permission_classes = [AllowAny]
    serializer_class = PasswordChangeSerializer
    
    @extend_schema(
        operation_id="v1_change_password_complete",
        tags=["auth_v1"],
    )
    def post(self, request, token):
        serializer = self.serializer_class(data=request.data, context={"token": token})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response("Password changed successfully.", status=status.HTTP_200_OK)


class KnoxLoginView(LoginView):
    throttle_classes = [AnonRateThrottle]
    permission_classes = [AllowAny]
    serializer_class = KnoxLoginSerializer

    @extend_schema(
        operation_id="v1_knox_login",
        tags=["auth_v1"],
    )
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

    @extend_schema(
        operation_id="v1_jwt_login",
        tags=["auth_v1"],
    )
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
            store_access_token.delay(login_data["access"])
            return Response(login_data, status=status.HTTP_200_OK)
        
       
@method_decorator([csrf_exempt, never_cache, psa("user:social-complete")], name="get")
class SocialAuthenticationBeginView(APIView):
    @extend_schema(
        operation_id="v1_social_authentication_begin",
        tags=["auth_v1"],
    )
    def get(self, request, backend):
        return begin_social_authentication(request, backend)
    
            
@method_decorator([csrf_exempt, never_cache, psa("user:social-complete")], name="get")
class SocialAuthenticationCompleteView(APIView):
    @extend_schema(
        operation_id="v1_social_authentication_complete",
        tags=["auth_v1"],
    )
    def get(self, request, backend):
        return complete_social_authentication(request, backend)


class JWTRefreshView(APIView):
    throttle_classes = [AnonRateThrottle]
    permission_classes = [AllowAny]
    serializer_class = RefreshTokenSerializer

    @extend_schema(
        operation_id="v1_jwt_refresh",
        tags=["auth_v1"],
    )
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

    @extend_schema(
        operation_id="v1_authentication_test",
        tags=["auth_v1"],
    )
    def get(self, request):
        return Response("Hello world.", status=status.HTTP_200_OK)


class KnoxLogoutView(APIView):
    throttle_classes = [UserRateThrottle]
    authentication_classes = [PaletteTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="v1_knox_logout_current_session",
        tags=["auth_v1"],
    )
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

    @extend_schema(
        operation_id="v1_jwt_logout",
        tags=["auth_v1"],
    )
    def post(self, request):
        refresh = SessionRefreshToken(request)
        refresh.remove()
        delete_access_token.delay(request.user.id)
        return Response("User logged out successfully.", status=status.HTTP_200_OK)


class KnoxLogoutAllView(LogoutAllView):
    throttle_classes = [UserRateThrottle]
    authentication_classes = [PaletteTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="v1_knox_logot_all_sessions",
        tags=["auth_v1"],
    )
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
    pagination_class = UserPagination

    @extend_schema(
        operation_id="v1_artist_list_retrieve",
        tags=["profile_v1"],
    )
    def get(self, request):
        cached_artists = cache.get("artist_list")
        if cached_artists is not None:
            artists = pickle.loads(cached_artists)
        else:
            artists = Artist.objects.all()
            cache.set("artist_list", pickle.dumps(artists))
            
        # Paginate the artists queryset
        paginator = self.pagination_class()
        paginated_artists = paginator.paginate_queryset(artists, request, view=self)
        artist_data = self.serializer_class(paginated_artists, many=True).data    
        return paginator.get_paginated_response(artist_data)
        
    @extend_schema(
        operation_id="v1_artist_create",
        tags=["profile_v1"],
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={"user": request.user})
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

    @extend_schema(
        operation_id="v1_artist_retrieve",
        tags=["profile_v1"],
    )
    def get(self, request, profile_id):
        artist = Artist.objects.filter(id=profile_id).first()
        artist_data = self.serializer_class(artist).data
        return Response(artist_data, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="v1_artist_update",
        tags=["profile_v1"],
    )
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
                
            artist_data = self.serializer_class(profile_data).data
            update_cache_details.delay(artist_data["id"], profile_id)
            return Response(artist_data, status=status.HTTP_202_ACCEPTED)

    @extend_schema(
        operation_id="v1_artist_delete",
        tags=["profile_v1"],
    )
    def delete(self, request, profile_id):
        artist = Artist.objects.filter(id=profile_id).first()
        with atomic():
            artist.delete()
            
        update_cache_details.delay(artist.id, profile_id, is_delete=True)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CollectorProfileListView(APIView):
    throttle_classes = [UserRateThrottle]
    authentication_classes = [PaletteTokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CollectorProfileSerializer
    pagination_class = UserPagination

    @extend_schema(
        operation_id="v1_collector_list_retrieve",
        tags=["profile_v1"],
    )
    def get(self, request):
        cached_collectors = cache.get("collector_list")
        if cached_collectors is not None:
            collectors = pickle.loads(cached_collectors)
        else:
            collectors = Collector.objects.all()
            cache.set("collector_list", pickle.dumps(collectors))
            
        # Paginate the collectors queryset
        paginator = self.pagination_class()
        paginated_collectors = paginator.paginate_queryset(collectors, request, view=self)
        collectors_data = self.serializer_class(paginated_collectors, many=True).data
        return paginator.get_paginated_response(collectors_data)

    @extend_schema(
        operation_id="v1_collector_create",
        tags=["profile_v1"],
    )
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

    @extend_schema(
        operation_id="v1_collector_retrieve",
        tags=["profile_v1"],
    )
    def get(self, request, profile_id):
        collector = Collector.objects.filter(id=profile_id).first()
        collector_data = self.serializer_class(collector).data
        return Response(collector_data, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="v1_collector_update",
        tags=["profile_v1"],
    )
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
                
            collector_data = self.serializer_class(profile_data).data
            update_cache_details.delay(collector_data["id"], profile_id, is_collector=True)
            return Response(collector_data, status=status.HTTP_202_ACCEPTED)

    @extend_schema(
        operation_id="v1_collector_delete",
        tags=["profile_v1"],
    )
    def delete(self, request, profile_id):
        collector = Collector.objects.filter(id=profile_id).first()
        with atomic():
            collector.delete()
            
        update_cache_details.delay(collector.id, profile_id, is_delete=True, is_collector=True)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CronJobAction(APIView):
    @extend_schema(
        operation_id="v1_cronjob",
        tags=["cronjob_v1"],
    )
    def get(self, request):
        return Response("Success", status=status.HTTP_200_OK)
