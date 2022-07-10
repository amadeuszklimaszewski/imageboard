from rest_framework import permissions


class UserHasAccountPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if getattr(user, "user_account", None):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if getattr(user, "user_account", None):
            return True
        return False


class UserCanGenerateTemporaryLinkPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        user_account = getattr(user, "user_account", None)
        membership_type = getattr(user_account, "membership_type", None)
        generates_expiring_link = getattr(
            membership_type, "generates_expiring_link", False
        )
        if generates_expiring_link:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        user_account = getattr(user, "user_account", None)
        membership_type = getattr(user_account, "membership_type", None)
        generates_expiring_link = getattr(
            membership_type, "generates_expiring_link", False
        )
        if generates_expiring_link:
            return True
        return False
