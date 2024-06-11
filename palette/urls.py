from django.urls import path
from .views import GenreList, ArtworkList, GenreDetail, ArtworkDetail


app_name = "palette"


urlpatterns = [
    path("genre/", GenreList.as_view(), name="genre-list"),
    path("genre/<slug:slug>/", GenreDetail.as_view(), name="genre-detail"),
    path("artwork/", ArtworkList.as_view(), name="artwork-list"),
    path("artwork/<slug:slug>/", ArtworkDetail.as_view(), name="artwork-detail"),
]
