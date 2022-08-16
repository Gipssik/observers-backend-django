from typing import Any

from django.db.models import QuerySet
from django_filters import rest_framework as filters
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response

from api.forum import serializers as forum_serializers
from api.forum.filters import QuestionFilter
from api.forum.permissions import (
    HasAccessToObjectOrReadOnly,
    HasAccessToUpdateCertainCommentField,
)
from common import mixins as common_mixins
from common.exceptions import UnprocessableEntity
from common.permissions import IsAdminUserOrReadOnly
from forum.models import Comment, Question, Tag


class TagViewSet(
    common_mixins.MultipleSerializersMixinSet,
    viewsets.ModelViewSet,
):
    """Set of tag views."""

    queryset = Tag.objects.all()
    permission_classes = [IsAdminUserOrReadOnly]

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.serializer_action_classes = {
            "list": forum_serializers.TagSerializer,
            "create": forum_serializers.TagBaseSerializer,
            "retrieve": forum_serializers.TagSerializer,
            "update": forum_serializers.TagBaseSerializer,
            "partial_update": forum_serializers.TagBaseSerializer,
        }

    def get_queryset(self) -> QuerySet[Tag]:
        """Returns queryset of tags prefetching questions and their tags.

        :return: Queryset of tags with prefetched questions.
        """
        return Tag.objects.all().prefetch_related("questions__tags")

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Returns tag by id or by its title.

        :param request: Current request.
        :param args: Args
        :param kwargs: Kwargs.
        :return: Response with tag.
        """
        pk = kwargs.get("pk", "")
        try:
            pk = int(pk)
        except ValueError:
            tag = get_object_or_404(self.get_queryset(), title=pk)
            serializer = self.get_serializer(tag)
            return Response(serializer.data)
        return super().retrieve(request, *args, **kwargs)


class QuestionViewSet(
    common_mixins.MultipleSerializersMixinSet,
    viewsets.ModelViewSet,
):
    """Set of question views."""

    queryset = Question.objects.all()
    serializer_class = forum_serializers.QuestionSerializer
    permission_classes = [
        HasAccessToObjectOrReadOnly,
    ]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = QuestionFilter

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.serializer_action_classes = {
            "create": forum_serializers.QuestionCreationSerializer,
            "update": forum_serializers.QuestionChangeSerializer,
            "partial_update": forum_serializers.QuestionChangeSerializer,
        }

    @property
    def paginator(self) -> Any:
        """Returns paginator object.

        :return: None if action is 'questions_by_user', if not calls superclass method.
        """
        return None if self.action == "questions_by_user" else super().paginator

    def get_queryset(self) -> QuerySet[Question]:
        """Returns queryset of questions prefetching their tags.

        :return: Queryset of questions with prefetched tags.
        """
        return Question.objects.all().prefetch_related("tags")

    @action(
        detail=True,
        methods=["PATCH"],
        url_path="views",
        name="update_views",
        url_name="update_views",
    )
    def update_question_views(
        self,
        request: Request,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        """Updates views counter on question.

        :param request: Current request.
        :param args: Args.
        :param kwargs: Kwargs.
        :return: Response with updated question.
        :raises UnprocessableEntity: if there were no views provided.
        """
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
    def questions_by_user(
        self,
        request: Request,
        user_id: str,
        *args,
        **kwargs,
    ) -> Response:
        """Returns all user's questions.

        :param request: Current request.
        :param user_id: User's ID.
        :param args: Args.
        :param kwargs: Kwargs.
        :return: Response with user's questions.
        """
        questions = Question.objects.filter(author_id=user_id).prefetch_related("tags")
        serializer = self.get_serializer(questions, many=True)
        return Response(serializer.data)


class CommentViewSet(
    common_mixins.MultipleSerializersMixinSet,
    viewsets.ModelViewSet,
):
    """Set of comment views."""

    queryset = Comment.objects.all()
    serializer_class = forum_serializers.CommentSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        HasAccessToObjectOrReadOnly,
        HasAccessToUpdateCertainCommentField,
    ]

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.serializer_action_classes = {
            "create": forum_serializers.CommentCreationSerializer,
            "update": forum_serializers.CommentChangeSerializer,
            "partial_update": forum_serializers.CommentChangeSerializer,
        }

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Returns all comments by question id.

        :param request: Current request.
        :param args: Args.
        :param kwargs: Kwargs.
        :return: Response with all question's comments.
        """
        question = get_object_or_404(Question.objects.all(), pk=kwargs.get("pk"))
        comments = question.comments.all()
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)
