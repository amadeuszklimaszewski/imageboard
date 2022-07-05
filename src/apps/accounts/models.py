import uuid
from django.db import models
from django.contrib.auth import get_user_model

from src.apps.memberships.models import MembershipType
from src.core.models import TimeStampedModel

User = get_user_model()


class UserAccount(TimeStampedModel):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="user_account"
    )
    membership_type = models.ForeignKey(
        MembershipType, on_delete=models.SET_NULL, null=True
    )

    def get_absolute_url(self):
        return f"/api/accounts/{self.id}/"

    @property
    def endpoint(self):
        return self.get_absolute_url()

    def __str__(self) -> str:
        return f"Profile of the user: {self.user.username}"
