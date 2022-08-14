from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView


class IsAdminUserOrReadOnly(permissions.IsAdminUser):
    """Check if user is admin or method is safe."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Checks if user is admin or this is read only operation.

        :param request: Current request.
        :param view: Current view.
        :return: True if user is admin or method is safe, otherwise - False.
        """
        return request.method in permissions.SAFE_METHODS or super().has_permission(
            request,
            view,
        )
