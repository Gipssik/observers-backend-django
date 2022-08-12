from rest_framework import permissions


class IsAdminUserOrReadOnly(permissions.IsAdminUser):
    """Check if user is admin or is method safe."""

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or super().has_permission(
            request, view
        )
