from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="UVAQ",
        default_version="1.0.0",
        description="API for the Universal Application Connection Hub",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

version = settings.API_VERSION

urlpatterns = [
    path("admin/", admin.site.urls),
    path(f"{version}/api/santander/", include("santander.urls")),
    path(f"{version}/api/uvaq/", include("uvaq.urls")),
    path(f"{version}/api/evoti/", include("evoti.urls")),
    path(f"{version}/authentication/", include("authentication.urls")),
    path(
        f"{version}/docs/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(f"{version}/redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
