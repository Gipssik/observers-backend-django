from rest_framework import permissions

from forum.models import Notification, Comment


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


class HasAccessToObjectOrReadOnly(permissions.BasePermission):
    """Check if current user is superuser or author of object"""

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_superuser
            or obj.author == request.user
        )


class HasAccessToUpdateCertainCommentField(permissions.BasePermission):
    def has_object_permission(self, request, view, obj: Comment):
        if request.user.is_superuser or request.method not in ("PATCH", "PUT"):
            return True

        if "content" in request.data and request.user != obj.author:
            return False
        # Only author of question can change field "is_answer"
        return "is_answer" not in request.data or request.user == obj.question.author
