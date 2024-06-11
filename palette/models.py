from django.db.models import (Model,UUIDField, CharField, SlugField,
                              DateTimeField, Index, ImageField, TextField,
                               PositiveIntegerField, URLField, ForeignKey, CASCADE,
                                BooleanField, ManyToManyField)
from django.db.models.manager import Manager
from uuid import uuid4


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
        indexes = [
            Index(fields=["id"]),
            Index(fields=["name"]),
            Index(fields=["slug"])
        ]
        
    def __str__(self):
        return self.name
    
    
class Artwork(Model):
    id = UUIDField(primary_key=True, editable=False, default=uuid4)
    name = CharField(max_length=250, unique=True)
    slug = SlugField(max_length=250, blank=True)
    description = TextField(blank=True)
    image = ImageField(upload_to="images/")
    artist = CharField(max_length=250)
    height = PositiveIntegerField(blank=True, null=True)
    width = PositiveIntegerField(blank=True, null=True)
    instagram = URLField(max_length=255, blank=True)
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