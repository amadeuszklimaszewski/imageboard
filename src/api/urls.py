from django.urls import path, include

urlpatterns = [
    path("", include("src.apps.accounts.urls", namespace="accounts")),
]
