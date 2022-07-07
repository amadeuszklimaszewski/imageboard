from django.db import models

from src.core.models import TimeStampedModel

# class TempUrl(models.Model):
#     url_hash = models.CharField("Url", blank=False, max_length=32, unique=True)
#     expires = models.DateTimeField("Expires")


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
