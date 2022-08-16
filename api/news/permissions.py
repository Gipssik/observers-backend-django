from rest_framework.request import Request
from rest_framework.views import APIView

from common.permissions import IsAdminUserOrReadOnly


class IsUpdatingRatingOrIsAdminUserOrReadOnly(IsAdminUserOrReadOnly):
    """Check if user is updating rating or this is superuser or read only operation."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Returns True if user is updating rating or returns superclass implementation.

        :param request: Current request.
        :param view: Current view.
        :return: Has user access or not.
        """
        action: str | None = getattr(view, "action", None)
        return action == "article_update_rating" or super().has_permission(
            request,
            view,
        )
