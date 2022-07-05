from django.db import models

from src.apps.images.models import ThumbnailSize
from src.core.models import TimeStampedModel


class MembershipType(TimeStampedModel):
    name = models.CharField(max_length=50, null=False, blank=False)

    thumbnail_sizes = models.ManyToManyField(ThumbnailSize)

    contains_original_link = models.BooleanField(default=False)
    generates_expiring_link = models.BooleanField(default=False)

    def get_absolute_url(self):
        return f"/api/memberships/{self.id}/"

    @property
    def endpoint(self):
        return self.get_absolute_url()

    def __str__(self) -> str:
        return f"Membership type: {self.name}"
