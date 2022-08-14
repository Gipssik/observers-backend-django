from typing import Any

from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView

from forum.models import Comment, Notification


class IsAdminOrNotificationDeletionByOwner(permissions.IsAdminUser):
    """Is user admin or is current user deleting own notification."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Checks if it is DELETE method.

        :param request: Current request.
        :param view: Current view.
        :return: True - if it is DELETE method, otherwise calls superclass' method.
        """
        return request.method == "DELETE" or super().has_permission(request, view)

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


class HasAccessToObjectOrReadOnly(permissions.BasePermission):
    """Check if current user is superuser or author of object."""

    def has_object_permission(
        self,
        request: Request,
        view: APIView,
        obj: Any,
    ) -> bool:
        """Checks if current user is superuser or author of object.

        :param request: Current request.
        :param view: Current view.
        :param obj: Model instance.
        :return: True - if user is owner or admin, otherwise - False.
        """
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_superuser
            or obj.author == request.user
        )


class HasAccessToUpdateCertainCommentField(permissions.BasePermission):
    """Check if user has access to change a certain comment field."""

    def has_object_permission(
        self,
        request: Request,
        view: APIView,
        obj: Comment,
    ) -> bool:
        """Checks if user has access to change a certain comment field.

        Superuser can change everything. Only author of comment can change its content.
        Only author of question can mark comment as answer.

        :param request: Current request.
        :param view: Current view.
        :param obj: Comment instance.
        :return: True - if user has access to change field, otherwise - False.
        """
        if request.user.is_superuser or request.method not in {"PATCH", "PUT"}:
            return True

        if "content" in request.data and request.user != obj.author:
            return False
        # Only author of question can change field "is_answer"
        return "is_answer" not in request.data or request.user == obj.question.author
