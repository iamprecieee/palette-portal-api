from django.db.models import (
    Model,
    UUIDField,
    CharField,
    SlugField,
    DateTimeField,
    Index,
    ImageField,
    TextField,
    PositiveIntegerField,
    URLField,
    DecimalField,
    BooleanField,
    ManyToManyField,
    ForeignKey,
    CASCADE,
)
from django.db.models.manager import Manager
from django.conf import settings

from user.models import Artist

from uuid import uuid4
from cloudinary.uploader import destroy


# Custom manager class for operating on available artworks
class AvailableManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_available=True)


class Genre(Model):
    id = UUIDField(primary_key=True, editable=False, default=uuid4)
    name = CharField(max_length=250, unique=True)
    slug = SlugField(max_length=250, blank=True)
    created = DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "genre"
        ordering = ["-created"]
        indexes = [Index(fields=["id"]), Index(fields=["name"]), Index(fields=["slug"])]

    def __str__(self):
        return self.name


class Artwork(Model):
    id = UUIDField(primary_key=True, editable=False, default=uuid4)
    name = CharField(max_length=250, unique=True)
    slug = SlugField(max_length=250, blank=True)
    description = TextField(blank=True)
    image = ImageField(upload_to="images/")
    artist = ForeignKey(Artist, related_name="artist_artworks", on_delete=CASCADE)
    height = PositiveIntegerField(blank=True, null=True)
    width = PositiveIntegerField(blank=True, null=True)
    price = DecimalField(decimal_places=2, max_digits=7, blank=True, null=True)
    genre = ManyToManyField(Genre, related_name="artworks", db_index=True)
    is_available = BooleanField(default=True)
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)

    objects = Manager()
    available = AvailableManager()

    class Meta:
        db_table = "artwork"
        ordering = ["-created"]
        indexes = [
            Index(fields=["id"]),
            Index(fields=["name"]),
            Index(fields=["slug"]),
            Index(fields=["artist"]),
            Index(fields=["is_available"]),
        ]

    def __str__(self):
        return self.name

    # Extending the `delete` method to also remove the deleted image from cloudinary
    def delete(self, *args, **kwargs):
        if self.image:
            public_id = self.image.name
            destroy(
                public_id=public_id,
                api_key=settings.CLOUDINARY_STORAGE["API_KEY"],
                api_secret=settings.CLOUDINARY_STORAGE["API_SECRET"],
                cloud_name=settings.CLOUDINARY_STORAGE["CLOUD_NAME"],
            )
        return super().delete(*args, **kwargs)
