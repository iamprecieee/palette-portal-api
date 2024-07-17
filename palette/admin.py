from django.contrib.admin import register, ModelAdmin

from .models import Genre, Artwork


@register(Genre)
class GenreAdmin(ModelAdmin):
    list_display = ["id", "name", "slug", "created"]
    list_filter = ["name", "created"]
    prepopulated_fields = {"slug": ["name"]}


@register(Artwork)
class ArtworkAdmin(ModelAdmin):
    list_display = [
        "id",
        "name",
        "slug",
        "description",
        "image",
        "artist",
        "height",
        "width",
        "is_available",
        "created",
        "updated",
    ]
    list_filter = ["name", "created"]
    prepopulated_fields = {"slug": ["name"]}
    filter_horizontal = ["genre"]
