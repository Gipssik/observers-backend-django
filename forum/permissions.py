from typing import Any

from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView

from forum.models import Comment


class HasAccessToObjectOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """Check if current user is superuser or author of object."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Checks if user is updating question views.

        :param request: Current request.
        :param view: Current view.
        :return: True - if user is updating question views,
         otherwise - calls superclass method.
        """
        action = getattr(view, "action")
        if action == "update_question_views":
            return True
        return super().has_permission(request, view)

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
        action = getattr(view, "action")
        if action == "update_question_views":
            return True
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
