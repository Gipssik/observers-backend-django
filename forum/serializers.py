from rest_framework import serializers

from authentication.models import User
from forum.models import Notification, Tag, Question, Comment


class NotificationBaseSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=256, required=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    question_id = serializers.PrimaryKeyRelatedField(queryset=Question.objects.all())

    def create(self, validated_data: dict) -> Notification:
        return Notification.objects.create(**validated_data)

    def update(self, instance: Notification, validated_data: dict) -> Notification:
        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance


class NotificationSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    question_id = serializers.PrimaryKeyRelatedField(queryset=Question.objects.all())

    class Meta:
        model = Notification
        exclude = ["user", "question"]


class QuestionCreationSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        many=True, slug_field="title", queryset=Tag.objects.all()
    )
    author_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Question
        fields = ["title", "content", "tags", "author_id"]

    def create(self, validated_data: dict):
        # Set removes duplicates + db works faster with sets
        tags = set(validated_data.pop("tags"))
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


class TagBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["title"]


class QuestionSerializer(serializers.ModelSerializer):
    tags = TagBaseSerializer(many=True)
    author_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Question
        exclude = ["author"]


class TagSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Tag
        fields = ["id", "title", "questions"]


class CommentCreationSerializer(serializers.ModelSerializer):
    author_id = serializers.PrimaryKeyRelatedField(
        required=False, default=None, queryset=User.objects.all()
    )

    class Meta:
        model = Comment
        fields = ["content", "question_id", "author_id"]


class CommentChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["content", "is_answer"]


class CommentSerializer(serializers.ModelSerializer):
    author_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Comment
        exclude = ["author"]
