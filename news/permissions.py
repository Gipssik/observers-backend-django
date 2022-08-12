from common.permissions import IsAdminUserOrReadOnly


class IsUpdatingRatingOrIsAdminUserOrReadOnly(IsAdminUserOrReadOnly):
    def has_permission(self, request, view):
        if view.action == "article_update_rating":
            return True

        return super().has_permission(request, view)
