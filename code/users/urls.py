from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView,
    ProfileView,
    UserViewSet,
    UserSearchByGameView,
    GamerProfileViewSet,
    FriendRequestViewSet,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    LogoutView,
)

# 👇 DRF router for the ViewSet
router = DefaultRouter()
router.register(
    r"", UserViewSet, basename="users"
)  # note: no 'users/' prefix since you're under api/users/
router.register(r"profile", GamerProfileViewSet, basename="gamer-profile")
router.register(r"friends", FriendRequestViewSet, basename="friend-request")
urlpatterns = [
    # Auth views
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("me/", ProfileView.as_view(), name="profile"),
    path("search-by-game/", UserSearchByGameView.as_view(), name="search-by-game"),
    path("logout/", LogoutView.as_view(), name="logout"),
]

# 👇 Add ViewSet-generated URLs to urlpatterns
urlpatterns += router.urls
