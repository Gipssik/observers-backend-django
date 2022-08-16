from typing import Any

from django.contrib.auth.base_user import AbstractBaseUser
from django.db.models import QuerySet
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from api.news import serializers as news_serializers
from api.news.permissions import IsUpdatingRatingOrIsAdminUserOrReadOnly
from api.news.types import UpdateAction
from authentication.models import User
from common import mixins as common_mixins
from common.exceptions import UnprocessableEntity
from news.models import Article


class ArticleViewSet(
    common_mixins.MultipleSerializersMixinSet,
    viewsets.ModelViewSet,
):
    """Set of article views."""

    queryset = Article.objects.all()
    serializer_class = news_serializers.ArticleSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsUpdatingRatingOrIsAdminUserOrReadOnly,
    ]

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.serializer_action_classes = {
            "create": news_serializers.ArticleBaseSerializer,
            "update": news_serializers.ArticleBaseSerializer,
            "partial_update": news_serializers.ArticleBaseSerializer,
        }

    @action(
        detail=True,
        methods=["PATCH"],
        url_path=r"(?P<update_action>\w+)",
        name="update_rating",
        url_name="update_rating",
    )
    def article_update_rating(
        self,
        request: Request,
        update_action: str,
        *args,
        **kwargs,
    ) -> Response:
        """Updates article's rating.

        :param request: Current request.
        :param update_action: Update action as a string - 'likes' or 'dislikes'.
        :param args: Args.
        :param kwargs: Kwargs.
        :return: Response with updated article.
        :raises UnprocessableEntity: if invalid update_action was provided.
        """
        if update_action not in UpdateAction.tuple():
            raise UnprocessableEntity

        article: Article = self.get_object()
        current_user = request.user
        current_action_attr = getattr(article, update_action)
        current_action_users: QuerySet[User] = current_action_attr.all()

        if current_user in current_action_users:
            current_action_attr.remove(current_user)
        else:
            current_action_attr.add(current_user)
            self._process_other_action_user_deletion(
                article,
                current_user,
                update_action,
            )

        serializer = self.get_serializer(article)

        return Response(serializer.data)

    @staticmethod
    def _process_other_action_user_deletion(
        article: Article,
        user: AbstractBaseUser,
        current_action: str,
    ) -> None:
        action_types = UpdateAction.tuple()
        other_action = action_types[action_types.index(current_action) - 1]
        other_action_attr = getattr(article, other_action)
        other_action_users = other_action_attr.all()
        if user in other_action_users:
            other_action_attr.remove(user)
