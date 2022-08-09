from django.db import IntegrityError
from django.http import Http404
from rest_framework import serializers

from forum.models import Notification, Tag, Question, Comment


class NotificationBaseSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=256, required=True)
    user_id = serializers.IntegerField(required=True)
    question_id = serializers.IntegerField(required=True)

    def create(self, validated_data: dict) -> Notification:
        try:
            notification = Notification.objects.create(**validated_data)
        except IntegrityError as err:
            raise Http404 from err
        else:
            return notification

    def update(self, instance: Notification, validated_data: dict) -> Notification:
        for key, value in validated_data.items():
            setattr(instance, key, value)

        try:
            instance.save()
        except IntegrityError as err:
            raise Http404 from err
        else:
            return instance


class NotificationSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True)
    question_id = serializers.IntegerField(required=True)

    class Meta:
        model = Notification
        exclude = ["user", "question"]


class QuestionCreationSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(child=serializers.CharField(max_length=64))
    author_id = serializers.IntegerField(required=True)

    class Meta:
        model = Question
        fields = ["title", "content", "tags", "author_id"]


class QuestionChangeSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(child=serializers.CharField(max_length=64))

    class Meta:
        model = Question
        fields = ["title", "content", "tags", "views"]


class TagBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["title"]


class QuestionSerializer(serializers.ModelSerializer):
    tags = TagBaseSerializer(many=True)
    author_id = serializers.IntegerField(required=True)

    class Meta:
        model = Question
        exclude = ["author"]


class TagSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Tag
        fields = ["id", "title", "questions"]


class CommentCreationSerializer(serializers.ModelSerializer):
    author_id = serializers.IntegerField(required=False, default=None)

    class Meta:
        model = Comment
        fields = ["content", "question_id", "author_id"]


class CommentChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["content", "is_answer"]


class CommentSerializer(serializers.ModelSerializer):
    author_id = serializers.IntegerField(required=True)

    class Meta:
        model = Comment
        exclude = ["author"]
