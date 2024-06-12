from django.urls import path

from .views import (
    GenreList,
    ArtworkList,
    GenreDetail,
    ArtworkDetail,
    CartList,
    CartDetail,
)


app_name = "palette"


urlpatterns = [
    path("genre/", GenreList.as_view(), name="genre-list"),
    path("genre/<slug:slug>/", GenreDetail.as_view(), name="genre-detail"),
    path("artwork/", ArtworkList.as_view(), name="artwork-list"),
    path("artwork/<slug:slug>/", ArtworkDetail.as_view(), name="artwork-detail"),
    path("cart/", CartList.as_view(), name="cart-list"),
    path("cart/<uuid:id>/", CartDetail.as_view(), name="cart-detail"),
]
