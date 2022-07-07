import io
import os
from typing import Any
from django.db import transaction
from django.core.files.base import ContentFile
from PIL import Image

from src.apps.images.exceptions import UnsupportedFileExtension
from src.apps.accounts.models import UserAccount
from src.apps.images.models import Thumbnail, Image as ImageModel
from src.apps.images.utils import (
    get_thumbnail_dimensions,
    get_format,
    get_thumbnail_filename,
)


class ImageService:
    @classmethod
    def create_thumbnail(
        self, instance: ImageModel, thumbnail_size: tuple[int]
    ) -> Thumbnail:
        image = instance.image
        image_file = Image.open(image.path)

        image_file.thumbnail(thumbnail_size, Image.ANTIALIAS)

        image_filename = os.path.basename(image.name)
        name, extension = image_filename.split(".")

        thumbnail_filename = get_thumbnail_filename(
            name=name, extension=extension, size=thumbnail_size
        )
        format = get_format(extension=extension)
        if not format:
            raise UnsupportedFileExtension(
                "We do not provide support for this file extension."
            )
        temporary_thumbnail = io.BytesIO()
        image_file.save(temporary_thumbnail, format)
        file = ContentFile(temporary_thumbnail.getvalue(), name=thumbnail_filename)
        temporary_thumbnail.close()

        thumbnail = Thumbnail.objects.create(image=instance, thumbnail=file)
        return thumbnail

    @classmethod
    @transaction.atomic
    def upload_image(
        cls, data: dict[str, Any], user_account: UserAccount
    ) -> ImageModel:
        title = data["title"]
        image_file = data["image"]
        print(image_file)
        image_model = ImageModel.objects.create(
            image=image_file, title=title, uploaded_by=user_account
        )
        thumbnail_sizes = user_account.membership_type.thumbnail_sizes.all()

        for thumbnail_size in thumbnail_sizes:
            size = get_thumbnail_dimensions(
                image_height=image_model.height,
                image_width=image_model.width,
                thumbnail_height=thumbnail_size.height,
            )
            cls.create_thumbnail(instance=image_model, thumbnail_size=size)
        return image_model
