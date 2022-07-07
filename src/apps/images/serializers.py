from rest_framework import serializers
from src.apps.images.models import Image, Thumbnail


class ImageInputSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    image = serializers.ImageField()


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


class ImageOutputSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Image
        fields = (
            "id",
            "title",
            "image",
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
    temporary_link_generator = serializers.SerializerMethodField()

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

    def get_temporary_link_generator(self, obj):
        return "test link"
