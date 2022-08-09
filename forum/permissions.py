from rest_framework import permissions

from forum.models import Notification


class IsAdminOrNotificationDeletionByOwner(permissions.IsAdminUser):
    """Is user admin or is current user deleting own notification."""

    def has_permission(self, request, view):
        return request.method == "DELETE" or super().has_permission(request, view)

    def has_object_permission(self, request, view, obj: Notification):
        return (
            request.method == "DELETE"
            and obj.user == request.user
            or request.user.is_superuser
        )


class IsAdminUserOrReadOnly(permissions.IsAdminUser):
    """Check if user is admin or is method safe."""

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or super().has_permission(
            request, view
        )
