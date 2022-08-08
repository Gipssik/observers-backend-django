from rest_framework import permissions

from authentication.models import User


class CanChangeUserOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow users to change only their account.
    """

    def has_object_permission(self, request, view, obj: User) -> bool:
        return bool(
            request.method in permissions.SAFE_METHODS
            or request.user.is_superuser
            or request.user == obj
        )
