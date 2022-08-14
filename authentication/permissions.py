from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView

from authentication.models import User


class CanChangeUserOrReadOnly(permissions.BasePermission):
    """Custom permission to allow users change only their account."""

    def has_object_permission(
        self,
        request: Request,
        view: APIView,
        obj: User,
    ) -> bool:
        """Checks if current user is the user wanted to change.

        :param request: Current request.
        :param view: Current view.
        :param obj: User instance.
        :return: True - if method is safe, user is admin or current user is that user,
         otherwise - False.
        """
        return bool(
            request.method in permissions.SAFE_METHODS
            or request.user.is_superuser
            or request.user == obj,
        )
