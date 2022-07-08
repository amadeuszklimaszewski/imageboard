from typing import Any
from rest_framework import serializers
from src.apps.images.models import Image, ImageAccessToken, Thumbnail


class ImageInputSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    image = serializers.ImageField()


class TemporaryLinkInputSerializer(serializers.Serializer):
    seconds = serializers.IntegerField()

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        if data["seconds"] < 300 or data["seconds"] > 30000:
            raise serializers.ValidationError(
                "Please use a value between 300 and 30000"
            )
        return data


class TemporaryImageOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ("image",)
        read_only_fields = fields


class TemporaryLinkOutputSerializer(serializers.ModelSerializer):
    img_url = serializers.HyperlinkedIdentityField(
        view_name="images:temporary-image", lookup_field="pk", read_only=True
    )

    class Meta:
        model = ImageAccessToken
        fields = (
            "img_url",
            "expires",
        )
        read_only_fields = fields


class ThumbnailOutputSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Thumbnail
        fields = (
            "height",
            "thumbnail",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class BasicImageOutputSerializer(serializers.ModelSerializer):
    thumbnails = ThumbnailOutputSerializer(many=True, read_only=True)

    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Image
        fields = (
            "id",
            "title",
            "thumbnails",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class PremiumImageOutputSerializer(serializers.ModelSerializer):
    thumbnails = ThumbnailOutputSerializer(many=True, read_only=True)

    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Image
        fields = (
            "id",
            "title",
            "thumbnails",
            "image",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class EnterpriseImageOutputSerializer(serializers.ModelSerializer):
    thumbnails = ThumbnailOutputSerializer(many=True, read_only=True)
    temporary_link_generator = serializers.HyperlinkedIdentityField(
        view_name="images:generate-image-link", lookup_field="pk", read_only=True
    )

    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Image
        fields = (
            "id",
            "title",
            "thumbnails",
            "image",
            "temporary_link_generator",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields
