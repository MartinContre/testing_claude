from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SantanderCredentialViewSet

router = DefaultRouter()
router.register(
    r"credentials", SantanderCredentialViewSet, basename="santander-credential"
)

urlpatterns = [
    path("", include(router.urls)),
]
