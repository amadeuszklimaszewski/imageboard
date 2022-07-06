from rest_framework import serializers
from src.apps.images.models import ThumbnailSize
from src.apps.memberships.models import MembershipType


class ThumbnailSizesOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThumbnailSize
        fields = ("height",)


class MembershipTypeOutputSerializer(serializers.ModelSerializer):
    thumbnail_sizes = ThumbnailSizesOutputSerializer(many=True, read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = MembershipType
        fields = (
            "name",
            "thumbnail_sizes",
            "contains_original_link",
            "generates_expiring_link",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields
