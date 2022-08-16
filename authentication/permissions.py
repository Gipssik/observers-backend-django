from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView

from authentication.models import Notification, User


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


class IsAdminOrNotificationDeletionByOwner(permissions.IsAdminUser):
    """Is user admin or is current user deleting own notification."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Checks if it is DELETE method.

        :param request: Current request.
        :param view: Current view.
        :return: True - if it is DELETE method, otherwise calls superclass' method.
        """
        action = getattr(view, "action")
        return (
            request.method == "DELETE"
            or action == "retrieve"
            or super().has_permission(request, view)
        )

    def has_object_permission(
        self,
        request: Request,
        view: APIView,
        obj: Notification,
    ) -> bool:
        """Checks if user can delete notification.

        :param request: Current request.
        :param view: Current view.
        :param obj: Notification instance.
        :return: True - if it is user's notification or user is admin, if not - False.
        """
        return (
            request.method == "DELETE"
            and obj.user == request.user
            or request.user.is_superuser
        )
