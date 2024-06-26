from django.db.transaction import atomic
from django.db import IntegrityError

from .models import User, Artist, Collector, PaletteAuthToken
from .refresh import SessionRefreshToken

from rest_framework.serializers import (
    ModelSerializer,
    CharField,
    ValidationError,
    EmailField,
    Serializer,
    SerializerMethodField,
)
from rest_framework.authentication import authenticate
from rest_framework.exceptions import AuthenticationFailed
import re
from rest_framework_simplejwt.tokens import RefreshToken


class RegisterSerializer(ModelSerializer):
    password = CharField(write_only=True)
    confirm_password = CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "username", "password", "confirm_password"]
        read_only_fields = ["id"]

    def validate(self, data):
        password = data["password"]
        confirm_password = data["confirm_password"]

        if len(password) < 8:
            raise ValidationError(
                {"password": "Password must contain at least 8 characters."}
            )

        if not re.search(r"[0-9]", password):
            raise ValidationError(
                {"password": "Password must contain at least 1 number."}
            )

        if not re.search(r"[A-Z]", password):
            raise ValidationError(
                {"password": "Password must contain at least 1 uppercase letter."}
            )

        if not re.search(r'[!@#$%^&*()_+=,.?/\|":;`~]', password):
            raise ValidationError(
                {"password": "Password must contain at least 1 symbol."}
            )

        if password != confirm_password:
            raise ValidationError({"password": "Passwords do not match."})

        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")

        return User.objects.create_user(**validated_data)


class LoginSerializer(ModelSerializer):
    """
    Serializer for knox-based login.
    Updates `last_login` and deletes extra auth tokens.
    """

    email = EmailField()
    password = CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "username", "password"]
        read_only_fields = ["id", "username"]

    def authenticate_user(self):
        request = self.context["request"]
        email = request.data["email"]
        password = request.data["password"]
        user = authenticate(request, email=email, password=password)
        if not user:
            raise AuthenticationFailed(
                "No active account found with the given credentials."
            )

        user.save(update_fields=["last_login"])
        with atomic():
            if PaletteAuthToken.objects.filter(user=user).count() == 3:
                PaletteAuthToken.objects.filter(user=user).last().delete()
            _, token = PaletteAuthToken.objects.create(user)

        return user, token


class RefreshTokenSerializer(Serializer):
    """
    Serializer for generating new access tokens, and blacklisting refresh tokens.
    Previous refresh token is blacklisted and replaced by a new token.
    """

    token_class = RefreshToken
    access = CharField(read_only=True)
    refresh = CharField(read_only=True)

    def validate(self):
        context = self.context
        session_refresh = SessionRefreshToken(context["request"])
        refresh = self.token_class(context["refresh"])
        access_data = {"access": str(refresh.access_token)}
        access_data["refresh"] = str(refresh)

        session_refresh.remove()
        session_refresh.add(access_data["refresh"])

        return access_data
    
    
class ArtistProfileSerializer(ModelSerializer):
    user = SerializerMethodField()
    class Meta:
        model = Artist
        fields = ["id", "bio", "instagram", "user"]
        read_only_fields = ["id"]
        
    def get_user(self, obj):
        return str(obj.user)
        
    def save(self):
        user = self.context["user"]
        validated_data = self.validated_data
        validated_data["user"] = user
        try:
            profile = Artist.objects.create(**validated_data)
        except IntegrityError:
            raise IntegrityError("This user has an existing artist profile.")
        
        return profile
        
        
class CollectorProfileSerializer(ModelSerializer):
    user = SerializerMethodField()
    class Meta:
        model = Collector
        fields = ["id", "bio", "instagram", "user"]
        read_only_fields = ["id"]
        
    def get_user(self, obj):
        return str(obj.user)
        
    def save(self):
        user = self.context["user"]
        validated_data = self.validated_data
        validated_data["user"] = user
        try:
            profile = Collector.objects.create(**validated_data)
        except IntegrityError:
            raise IntegrityError("This user has an existing collector profile.")
        
        return profile
