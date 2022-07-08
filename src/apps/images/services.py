import io
import os
from datetime import timedelta
from typing import Any
from uuid import UUID
from django.db import transaction
from django.core.files.base import ContentFile
from PIL import Image
from django.shortcuts import get_object_or_404
from django.utils import timezone

from src.apps.images.exceptions import InvalidImageAccessToken, UnsupportedFileExtension
from src.apps.accounts.models import UserAccount
from src.apps.images.models import ImageAccessToken, Thumbnail, Image as ImageModel
from src.apps.images.utils import (
    get_thumbnail_dimensions,
    get_format,
    get_thumbnail_filename,
    get_new_image_name,
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

        new_name = get_new_image_name(image_file.name)
        image_file.name = new_name

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


class TemporaryLinkService:
    @classmethod
    @transaction.atomic
    def create_access_token(
        cls,
        image_id: UUID,
        data: dict[str, int],
    ) -> ImageAccessToken:
        image = get_object_or_404(ImageModel, id=image_id)

        seconds = data["seconds"]
        expires = timezone.now() + timedelta(seconds=seconds)
        token = ImageAccessToken.objects.create(image=image, expires=expires)
        return token

    @classmethod
    def _validate_access_token(cls, access_token: ImageAccessToken) -> ImageAccessToken:
        if access_token.expires < timezone.now():
            access_token.delete()
            raise InvalidImageAccessToken("Invalid access token")
        return

    @classmethod
    def get_image_from_token(cls, access_token_id: UUID) -> Image:
        access_token = get_object_or_404(ImageAccessToken, id=access_token_id)
        cls._validate_access_token(access_token)
        return access_token.image
