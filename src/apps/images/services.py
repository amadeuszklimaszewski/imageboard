import io
import os
from math import ceil
from typing import Any
from django.core.files.base import ContentFile
from PIL import Image as ImagePIL

from src.apps.accounts.models import UserAccount
from src.apps.images.models import Thumbnail, Image as ImageModel


class ImageService:
    @classmethod
    def create_thumbnail(
        self, instance: ImageModel, thumbnail_size: tuple[int]
    ) -> Thumbnail:
        img = instance.image
        img_file = ImagePIL.open(img.path)
        if img_file.mode not in ("L", "RGB", "RGBA"):
            img_file = img_file.convert("RGB")
        img_file.thumbnail(thumbnail_size, ImagePIL.ANTIALIAS)

        img_filename = os.path.basename(img.name)
        name, extension = img_filename.split(".")
        size = f"{thumbnail_size[0]}x{thumbnail_size[1]}"

        thumb_filename = f"{name}-thumbnail-{size}px.{extension}"

        if extension in ["jpg", "jpeg"]:
            FTYPE = "JPEG"
        elif extension == "png":
            FTYPE = "PNG"
        else:
            return False

        tmp_thumbnail = io.BytesIO()
        img_file.save(tmp_thumbnail, FTYPE)
        file = ContentFile(tmp_thumbnail.getvalue(), name=thumb_filename)
        tmp_thumbnail.close()
        thumbnail = Thumbnail.objects.create(image=instance, thumbnail=file)
        return thumbnail

    @classmethod
    def upload_image(
        cls, data: dict[str, Any], user_account: UserAccount
    ) -> ImageModel:
        title = data["title"]
        image_file = data["image"]
        image_model = ImageModel.objects.create(
            image=image_file, title=title, uploaded_by=user_account
        )
        thumbnails = user_account.membership_type.thumbnail_sizes.all()

        for thumbnail in thumbnails:
            height = thumbnail.height
            width = ceil(image_model.width / (image_model.height / height))
            print(height, width)
            cls.create_thumbnail(instance=image_model, thumbnail_size=(width, height))
        return image_model
