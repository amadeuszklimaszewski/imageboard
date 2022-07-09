from django.conf import settings
from django.urls import path, include

urlpatterns = [
    path("", include("src.apps.accounts.urls", namespace="accounts")),
    path("", include("src.apps.memberships.urls", namespace="memberships")),
    path("", include("src.apps.images.urls", namespace="images")),
]

if settings.DEBUG:
    from src.swagger import schema_view

    urlpatterns += [
        path(
            "swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="swagger"
        )
    ]
