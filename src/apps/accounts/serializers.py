from django.contrib.auth import get_user_model
from rest_framework import serializers
from src.apps.accounts.models import UserAccount


User = get_user_model()


class UserOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
        )
        read_only_fields = fields


class UserAccountOutputSerializer(serializers.ModelSerializer):
    user = UserOutputSerializer(many=False, read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = UserAccount
        fields = (
            "id",
            "user",
            "membership_type",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields
