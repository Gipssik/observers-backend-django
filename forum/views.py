from django_filters import rest_framework as filters
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from authentication.models import User
from common import mixins as common_mixins
from common.exceptions import UnprocessableEntity
from common.permissions import IsAdminUserOrReadOnly
from forum.filters import QuestionFilter
from forum.models import Notification, Tag, Question, Comment
from forum.permissions import (
    IsAdminOrNotificationDeletionByOwner,
    HasAccessToObjectOrReadOnly,
    HasAccessToUpdateCertainCommentField,
)
from forum import serializers as forum_serializers


class NotificationViewSet(
    common_mixins.MultipleSerializersMixinSet,
    viewsets.ModelViewSet,
):
    queryset = Notification.objects.all()
    permission_classes = [IsAdminOrNotificationDeletionByOwner]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serializer_action_classes = {
            "list": forum_serializers.NotificationSerializer,
            "create": forum_serializers.NotificationBaseSerializer,
            "retrieve": forum_serializers.NotificationSerializer,
            "update": forum_serializers.NotificationBaseSerializer,
            "partial_update": forum_serializers.NotificationBaseSerializer,
        }

    def retrieve(self, request, *args, **kwargs):
        """Returns all user's notifications."""

        u: User = get_object_or_404(
            User.objects.all().prefetch_related("notifications"), pk=kwargs.get("pk")
        )
        serializer = self.get_serializer(u.notifications.all(), many=True)
        return Response(serializer.data)


class TagViewSet(
    common_mixins.MultipleSerializersMixinSet,
    viewsets.ModelViewSet,
):
    queryset = Tag.objects.all()
    permission_classes = [IsAdminUserOrReadOnly]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serializer_action_classes = {
            "list": forum_serializers.TagSerializer,
            "create": forum_serializers.TagBaseSerializer,
            "retrieve": forum_serializers.TagSerializer,
            "update": forum_serializers.TagBaseSerializer,
            "partial_update": forum_serializers.TagBaseSerializer,
        }

    def get_queryset(self):
        return Tag.objects.all().prefetch_related("questions__tags")


class QuestionViewSet(
    common_mixins.MultipleSerializersMixinSet,
    viewsets.ModelViewSet,
):
    queryset = Question.objects.all()
    serializer_class = forum_serializers.QuestionSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        HasAccessToObjectOrReadOnly,
    ]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = QuestionFilter

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serializer_action_classes = {
            "create": forum_serializers.QuestionCreationSerializer,
            "update": forum_serializers.QuestionChangeSerializer,
            "partial_update": forum_serializers.QuestionChangeSerializer,
        }

    @property
    def paginator(self):
        return None if self.action in ["questions_by_user"] else super().paginator

    def get_queryset(self):
        return Question.objects.all().prefetch_related("tags")

    @action(
        detail=True,
        methods=["PATCH"],
        url_path="views",
        name="update_views",
        url_name="update_views",
    )
    def update_question_views(self, request, *args, **kwargs):
        """Updates views counter on question."""
        # Front-end requires this endpoint for some reason.

        try:
            views = request.query_params["views"]
        except KeyError as err:
            raise UnprocessableEntity from err

        question: Question = self.get_object()
        question.views = views
        question.save()

        serializer = self.get_serializer(question)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["GET"],
        url_path=r"(?P<user_id>\w+)/user",
        name="by_user",
        url_name="by_user",
    )
    def questions_by_user(self, request, user_id, *args, **kwargs):
        """Returns all user's questions."""

        questions = Question.objects.filter(author_id=user_id).prefetch_related("tags")
        serializer = self.get_serializer(questions, many=True)
        return Response(serializer.data)


class CommentViewSet(
    common_mixins.MultipleSerializersMixinSet,
    viewsets.ModelViewSet,
):
    queryset = Comment.objects.all()
    serializer_class = forum_serializers.CommentSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        HasAccessToObjectOrReadOnly,
        HasAccessToUpdateCertainCommentField,
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serializer_action_classes = {
            "create": forum_serializers.CommentCreationSerializer,
            "update": forum_serializers.CommentChangeSerializer,
            "partial_update": forum_serializers.CommentChangeSerializer,
        }

    def retrieve(self, request, *args, **kwargs):
        """Returns all comments by question id."""

        question = get_object_or_404(Question.objects.all(), pk=kwargs.get("pk"))
        comments = question.comments.all()
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)
