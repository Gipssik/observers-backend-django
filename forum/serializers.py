from rest_framework import serializers

from authentication.models import User
from common.exceptions import UnprocessableEntity
from forum.models import Notification, Tag, Question, Comment


class NotificationBaseSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="user"
    )
    question_id = serializers.PrimaryKeyRelatedField(
        queryset=Question.objects.all(), source="question"
    )

    class Meta:
        model = Notification
        fields = ["title", "user_id", "question_id"]


class NotificationSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(read_only=True)
    question_id = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Notification
        exclude = ["user", "question"]


class QuestionCreationSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        many=True, slug_field="title", queryset=Tag.objects.all()
    )
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False, source="author"
    )

    class Meta:
        model = Question
        fields = ["title", "content", "tags", "author_id"]

    def create(self, validated_data: dict):
        # Set removes duplicates + db works faster with sets
        tags = set(validated_data.pop("tags"))

        if "author" not in validated_data:
            request = self.context.get("request")
            if not hasattr(request, "user"):
                raise UnprocessableEntity
            validated_data["author"] = request.user

        question = Question.objects.create(**validated_data)

        question.tags.set(tags)
        return question


class QuestionChangeSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        many=True, slug_field="title", queryset=Tag.objects.all()
    )

    class Meta:
        model = Question
        fields = ["title", "content", "tags", "views"]

    def update(self, instance: Question, validated_data: dict):
        if not validated_data:
            return instance

        tags = validated_data.pop("tags", None)
        if tags is not None:
            # Set removes duplicates + db works faster with sets
            tags = set(tags)
            instance.tags.set(tags)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance


class QuestionSerializer(serializers.ModelSerializer):
    author_id = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Question
        exclude = ["author"]
        depth = 1


class TagBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["title"]


class TagSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Tag
        fields = ["id", "title", "questions"]


class CommentCreationSerializer(serializers.ModelSerializer):
    author_id = serializers.PrimaryKeyRelatedField(
        required=False,
        default=None,
        queryset=User.objects.all(),
        source="author",
    )
    question_id = serializers.PrimaryKeyRelatedField(
        queryset=Question.objects.all(), source="question"
    )

    class Meta:
        model = Comment
        fields = ["content", "question_id", "author_id"]

    @staticmethod
    def _create_notification(instance: Comment) -> Notification:
        """Creates notification for a comment."""

        username = instance.author.username
        question_title = instance.question.title
        return Notification.objects.create(
            title=f'User {username} commented your question: "{question_title}".',
            user=instance.author,
            question=instance.question,
        )

    def create(self, validated_data: dict):
        request = self.context.get("request")
        if not validated_data.get("author"):
            if not hasattr(request, "user"):
                raise UnprocessableEntity
            validated_data["author"] = request.user.id

        comment = Comment.objects.create(**validated_data)
        if request.user != comment.author:
            self._create_notification(comment)

        return comment


class CommentChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["content", "is_answer"]


class CommentSerializer(serializers.ModelSerializer):
    question_id = serializers.PrimaryKeyRelatedField(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        exclude = ["question", "author"]
