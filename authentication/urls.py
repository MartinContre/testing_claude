from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AuthorizedUserViewSet, LoginView

# Create a DefaultRouter instance for handling user-related URLs.
router = DefaultRouter()
router.register(r"users", AuthorizedUserViewSet, basename="authorizeduser")

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),  # Route for user login
    path("", include(router.urls)),  # Include all routes registered with the router
]
