from django.urls import path

from .views import (
    RegisterView,
    KnoxLoginView,
    JWTLoginView,
    MockLoginView,
    JWTRefreshView,
    KnoxLogoutView,
    JWTLogoutView,
    KnoxLogoutAllView,
    ArtistProfileListView,
    CollectorProfileListView,
    ArtistProfileDetailView,
    CollectorProfileDetailView,
    CronJobAction
)


app_name = "user"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login-knox/", KnoxLoginView.as_view(), name="knox-login"),
    path("login-jwt/", JWTLoginView.as_view(), name="jwt-login"),
    path("token/refresh/", JWTRefreshView.as_view(), name="token-refresh"),
    path("mock-login/", MockLoginView.as_view(), name="mock-login"),
    path("logout-knox/", KnoxLogoutView.as_view(), name="knox-logout"),
    path("logout-jwt/", JWTLogoutView.as_view(), name="jwt-logout"),
    path("logout-knox-all/", KnoxLogoutAllView.as_view(), name="batch-knox-logout"),
    path("profile/artist/", ArtistProfileListView.as_view(), name="artist-profile-list"),
    path("profile/artist/<str:profile_id>/", ArtistProfileDetailView.as_view(), name="artist-profile-detail"),
    path("profile/collector/", CollectorProfileListView.as_view(), name="collector-profile-list"),
    path("profile/collector/<str:profile_id>/", CollectorProfileDetailView.as_view(), name="collector-profile-detail"),
    path("cron-job/", CronJobAction.as_view(), name="cron-job"),
]
