from rest_framework.routers import DefaultRouter
from src.apps.images.views import ImageViewSet

app_name = "images"

router = DefaultRouter()
router.register(r"images", ImageViewSet, basename="image")
urlpatterns = router.urls
