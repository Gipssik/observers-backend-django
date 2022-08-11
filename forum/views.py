from rest_framework import views
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from authentication.models import User
from common import mixins as common_mixins
from forum.models import Notification, Tag, Question
from forum.permissions import (
    IsAdminOrNotificationDeletionByOwner,
    IsAdminUserOrReadOnly,
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serializer_action_classes = {
            "list": forum_serializers.QuestionSerializer,
            "create": forum_serializers.QuestionCreationSerializer,
            "retrieve": forum_serializers.QuestionSerializer,
            "update": forum_serializers.QuestionChangeSerializer,
            "partial_update": forum_serializers.QuestionChangeSerializer,
            "question_by_title": forum_serializers.QuestionSerializer,
        }

    def get_queryset(self):
        return Question.objects.all().prefetch_related("tags")

    @action(
        detail=False,
        url_path=r"<question_title>/title",
        name="by_title",
        url_name="by_title",
    )
    def question_by_title(self, request, question_title, *args, **kwargs):
        """Returns all questions that contain the given string."""

        print(request)
        print(question_title)
        print(args)
        print(kwargs)
        questions = Question.objects.filter(
            title__icontains=question_title
        ).prefetch_related("tags")
        serializer = forum_serializers.QuestionSerializer(questions, many=True)
        return Response(serializer.data)


# class QuestionByTitleView(views.APIView):
#     @staticmethod
#     def get(request, question_title, *args, **kwargs):
#         """Returns all questions that contain the given string."""
#
#         questions = Question.objects.filter(
#             title__icontains=question_title
#         ).prefetch_related("tags")
#         serializer = forum_serializers.QuestionSerializer(questions, many=True)
#         return Response(serializer.data)
