from django.db.models import QuerySet
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from authentication.models import User
from common import mixins as common_mixins
from common.exceptions import UnprocessableEntity
from news import serializers as news_serializers
from news.models import Article
from news.permissions import IsUpdatingRatingOrIsAdminUserOrReadOnly
from news.types import UpdateAction


class ArticleViewSet(
    common_mixins.MultipleSerializersMixinSet,
    viewsets.ModelViewSet,
):
    queryset = Article.objects.all()
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsUpdatingRatingOrIsAdminUserOrReadOnly,
    ]
    serializer_class = news_serializers.ArticleSerializer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serializer_action_classes = {
            "create": news_serializers.ArticleBaseSerializer,
            "update": news_serializers.ArticleBaseSerializer,
            "partial_update": news_serializers.ArticleBaseSerializer,
        }

    @staticmethod
    def _process_other_action_user_deletion(
        article: Article, user: User, current_action: str
    ) -> None:
        action_types = UpdateAction.tuple()
        other_action = action_types[action_types.index(current_action) - 1]
        other_action_attr = getattr(article, other_action)
        other_action_users = other_action_attr.all()
        if user in other_action_users:
            other_action_attr.remove(user)

    @action(
        detail=True,
        methods=["PATCH"],
        url_path=r"(?P<update_action>\w+)",
        name="update_rating",
        url_name="update_rating",
    )
    def article_update_rating(self, request, update_action, *args, **kwargs):
        """Updates article's rating."""

        if update_action not in UpdateAction.tuple():
            raise UnprocessableEntity

        article: Article = self.get_object()
        current_user: User = request.user
        current_action_attr = getattr(article, update_action)
        current_action_users: QuerySet[User] = current_action_attr.all()

        if current_user in current_action_users:
            current_action_attr.remove(current_user)
        else:
            current_action_attr.add(current_user)
            self._process_other_action_user_deletion(
                article, current_user, update_action
            )

        serializer = self.get_serializer(article)

        return Response(serializer.data)
