from django.urls import include, path
from rest_framework.routers import DefaultRouter
from src.apps.images.views import (
    GenerateTemporaryLinkAPIView,
    ImageViewSet,
    TemporaryImageLinkAPIView,
)

app_name = "images"

router = DefaultRouter()
router.register(r"images", ImageViewSet, basename="image")
urlpatterns = router.urls

urlpatterns += [
    path(
        "images/<uuid:pk>/generate-temporary-link/",
        GenerateTemporaryLinkAPIView.as_view(),
        name="generate-image-link",
    ),
    path(
        "imgtmp/<uuid:pk>/",
        TemporaryImageLinkAPIView.as_view(),
        name="temporary-image",
    ),
]
