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
