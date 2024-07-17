from django.urls import path

from .views import (
    GenreListView,
    ArtworkListView,
    GenreDetailView,
    ArtworkDetailView,
    CartListView,
    CartDetailView,
)


app_name = "palette"


urlpatterns = [
    path("genre/", GenreListView.as_view(), name="genre-list"),
    path("genre/<slug:slug>/", GenreDetailView.as_view(), name="genre-detail"),
    path("artwork/", ArtworkListView.as_view(), name="artwork-list"),
    path("artwork/<slug:slug>/", ArtworkDetailView.as_view(), name="artwork-detail"),
    path("cart/", CartListView.as_view(), name="cart-list"),
    path("cart/<str:artwork_id>/", CartDetailView.as_view(), name="cart-detail"),
]
