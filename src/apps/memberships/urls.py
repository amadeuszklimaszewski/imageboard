from rest_framework.routers import DefaultRouter
from src.apps.memberships.views import MembershipTypeViewSet

app_name = "memberships"

router = DefaultRouter()
router.register(r"memberships", MembershipTypeViewSet, basename="membership")
urlpatterns = router.urls
