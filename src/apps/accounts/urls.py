from django.urls import path
from rest_framework.routers import DefaultRouter
from dj_rest_auth.views import (
    LoginView,
    LogoutView,
)
from src.apps.accounts.views import UserAccountViewSet

app_name = "accounts"

router = DefaultRouter()
router.register(r"users", UserAccountViewSet, basename="user")
urlpatterns = router.urls

urlpatterns += [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
