from django.db.models import (
    Model,
    UUIDField,
    DateTimeField,
    EmailField,
    CharField,
    BooleanField,
    TextField,
    URLField,
    OneToOneField,
    CASCADE,
    ForeignKey,
    Index,
)
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)
from django.conf import settings

from .utils import generate_default_username, uuid4

from knox.settings import CONSTANTS
from knox.models import AuthTokenManager
from knox.auth import (
    TokenAuthentication,
    _,
    hash_token,
    binascii,
    exceptions,
    compare_digest,
)


class PaletteUserManager(BaseUserManager):
    def _create_user(self, email, username, password, **kwargs):
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email, password, username=generate_default_username(), **kwargs
    ):
        kwargs.setdefault("is_staff", True)
        kwargs.setdefault("is_superuser", True)
        return self._create_user(
            email=email, username=username, password=password, **kwargs
        )

    def create_user(self, email, username, password, **kwargs):
        return self._create_user(
            email=email, username=username, password=password, **kwargs
        )


class User(AbstractBaseUser, PermissionsMixin):
    id = UUIDField(primary_key=True, editable=False, default=uuid4)
    email = EmailField(max_length=200, unique=True, blank=False, db_index=True)
    username = CharField(max_length=250, unique=True, blank=False, db_index=True)
    password = CharField(max_length=255, editable=False, blank=False)
    is_staff = BooleanField(default=False)
    is_superuser = BooleanField(default=False)
    is_active = BooleanField(default=True)
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)
    last_login = DateTimeField(auto_now=True)

    objects = PaletteUserManager()

    USERNAME_FIELD = "email"

    class Meta:
        db_table = "user"
        ordering = ["-created"]

    def __str__(self):
        return self.username


class Artist(Model):
    id = UUIDField(primary_key=True, editable=False, default=uuid4)
    bio = TextField(blank=True)
    instagram = URLField(max_length=255, blank=True, db_index=True)
    user = OneToOneField(
        User, related_name="user_artist", on_delete=CASCADE, db_index=True
    )
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)

    class Meta:
        db_table = "artist"
        ordering = ["-created"]

    def __str__(self):
        return self.user.username


class Collector(Model):
    id = UUIDField(primary_key=True, editable=False, default=uuid4)
    bio = TextField(blank=True)
    instagram = URLField(max_length=255, blank=True, db_index=True)
    user = OneToOneField(
        User, related_name="user_collector", on_delete=CASCADE, db_index=True
    )
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)

    class Meta:
        db_table = "collector"
        ordering = ["-created"]

    def __str__(self):
        return self.user.username


# Authentication setup using Knox
class PaletteAuthToken(Model):
    digest = CharField(max_length=CONSTANTS.DIGEST_LENGTH, primary_key=True)
    token_key = CharField(max_length=CONSTANTS.TOKEN_KEY_LENGTH, db_index=True)
    user = ForeignKey(
        User,
        blank=False,
        null=False,
        related_name="palette_auth_token_set",
        on_delete=CASCADE,
        db_index=True,
    )
    created = DateTimeField(auto_now_add=True)
    expiry = DateTimeField(blank=True, null=True)

    objects = AuthTokenManager()

    class Meta:
        db_table = "authtoken"
        ordering = ["-created"]

    def __str__(self):
        return f"{self.digest}: {self.user}"


# Overriding Knox's TokenAuthentication to use PaletteAuthToken as the authentication token model
class PaletteTokenAuthentication(TokenAuthentication):
    model = PaletteAuthToken

    def authenticate_credentials(self, token):
        msg = _("Invalid token.")
        token = token.decode("utf-8")
        for auth_token in PaletteAuthToken.objects.filter(
            token_key=token[: CONSTANTS.TOKEN_KEY_LENGTH]
        ):
            if self._cleanup_token(auth_token):
                continue

            try:
                digest = hash_token(token)
            except (TypeError, binascii.Error):
                raise exceptions.AuthenticationFailed(msg)

            if compare_digest(digest, auth_token.digest):
                if settings.REST_KNOX["AUTO_REFRESH"] and auth_token.expiry:
                    self.renew_token(auth_token)

                return self.validate_user(auth_token)

        raise exceptions.AuthenticationFailed(msg)


# For manually blacklisting [stateless] access tokens
class JWTTokenBlacklist(Model):
    token = CharField(max_length=255, unique=True, db_index=True)
    user = ForeignKey(User, related_name="blacklisted_tokens", on_delete=CASCADE)
    created = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]
        indexes = [Index(fields=["token", "user"])]
