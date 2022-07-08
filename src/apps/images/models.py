from uuid import uuid4
from django.db import models

from src.core.models import TimeStampedModel


class Image(TimeStampedModel):
    title = models.CharField(max_length=200)
    uploaded_by = models.ForeignKey(
        "accounts.UserAccount", on_delete=models.SET_NULL, null=True
    )
    height = models.IntegerField(default=0)
    width = models.IntegerField(default=0)

    image = models.ImageField(
        upload_to="static/images", height_field="height", width_field="width"
    )

    def __str__(self) -> str:
        return f"Image: {self.title}"


class ImageAccessToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    image = models.ForeignKey(Image, on_delete=models.CASCADE, editable=False)
    expires = models.DateTimeField()


class ThumbnailSize(models.Model):
    height = models.IntegerField()

    def __str__(self) -> str:
        return f"Thumbnail heigth: {self.height}"


class Thumbnail(TimeStampedModel):
    image = models.ForeignKey(
        Image, on_delete=models.CASCADE, related_name="thumbnails"
    )

    height = models.IntegerField(default=0)
    width = models.IntegerField(default=0)
    thumbnail = models.ImageField(
        upload_to="static/thumbnails", height_field="height", width_field="width"
    )

    def __str__(self) -> str:
        return f"Thumbnail of image: {self.image.title} ({self.width} x {self.height})"
