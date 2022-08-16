from typing import Any

from rest_framework import serializers
from rest_framework.request import Request

from api.forum import utils
from authentication.models import User
from common.exceptions import UnprocessableEntity
from forum.models import Comment, Question, Tag


class QuestionCreationSerializer(serializers.ModelSerializer[Question]):
    """Handles question creation."""

    tags = serializers.ListField(child=serializers.CharField(), required=False)
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        source="author",
    )

    class Meta:
        model = Question
        fields = ["title", "content", "tags", "author_id"]

    def create(self, validated_data: dict[str, Any]) -> Question:
        """Creates new question.

        If author was not provided it uses request's user.

        :param validated_data: Validated question data.
        :return: Question instance.
        :raises UnprocessableEntity: if there is no request object.
        """
        if "author" not in validated_data:
            request: Request | None = self.context.get("request")
            if not request:
                raise UnprocessableEntity
            validated_data["author"] = request.user

        tags: list[str] | None = validated_data.pop("tags", None)
        question = Question.objects.create(**validated_data)

        if tags:
            # Set removes duplicates + db works faster with sets
            tags_db = utils.get_db_tags(set(tags))
            question.tags.set(tags_db)

        return question


class QuestionChangeSerializer(serializers.ModelSerializer[Question]):
    """Handles question changing."""

    tags = serializers.ListField(child=serializers.CharField(), required=False)

    class Meta:
        model = Question
        fields = ["title", "content", "tags", "views"]

    def update(self, instance: Question, validated_data: dict[str, Any]) -> Question:
        """Updates question instance.

        :param instance: Question instance.
        :param validated_data: New validated question data.
        :return: Update Question instance.
        """
        if not validated_data:
            return instance

        tags = validated_data.pop("tags", None)
        if tags is not None:
            # Set removes duplicates + db works faster with sets
            tags: set[str] = set(tags)
            tags_db = utils.get_db_tags(tags)
            instance.tags.set(tags_db)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance


class QuestionSerializer(serializers.ModelSerializer[Question]):
    """Handles question retrieving."""

    author_id = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Question
        exclude = ["author"]
        depth = 1


class TagBaseSerializer(serializers.ModelSerializer[Tag]):
    """Handles create and update operations."""

    class Meta:
        model = Tag
        fields = ["title"]


class TagSerializer(serializers.ModelSerializer[Tag]):
    """Handles tag retrieving."""

    questions = QuestionSerializer(many=True)

    class Meta:
        model = Tag
        fields = ["id", "title", "questions"]


class CommentCreationSerializer(serializers.ModelSerializer[Comment]):
    """Handles comment creation."""

    author_id = serializers.PrimaryKeyRelatedField(
        required=False,
        default=None,
        queryset=User.objects.all(),
        source="author",
    )
    question_id = serializers.PrimaryKeyRelatedField(
        queryset=Question.objects.all(),
        source="question",
    )

    class Meta:
        model = Comment
        fields = ["content", "question_id", "author_id"]

    def create(self, validated_data: dict[str, Any]) -> Comment:
        """Creates a comment.

        If request's user is not the author of question, it creates a notification.

        :param validated_data: Validated comment data.
        :return: Comment instance.
        :raises UnprocessableEntity: if there is no request object.
        """
        request: Request | None = self.context.get("request")
        if not request:
            raise UnprocessableEntity
        if not validated_data.get("author"):
            validated_data["author"] = request.user.id

        comment = Comment.objects.create(**validated_data)
        if request.user != comment.question.author:
            utils.create_notification(comment)

        return comment


class CommentChangeSerializer(serializers.ModelSerializer[Comment]):
    """Handles comment changing."""

    class Meta:
        model = Comment
        fields = ["content", "is_answer"]


class CommentSerializer(serializers.ModelSerializer[Comment]):
    """Handles comment retrieving."""

    question_id = serializers.PrimaryKeyRelatedField(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        exclude = ["question", "author"]
