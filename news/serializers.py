from rest_framework import serializers

from news.models import Article


class ArticleBaseSerializer(serializers.ModelSerializer[Article]):
    """Article serializer to handle create and update operations."""

    class Meta:
        model = Article
        fields = ["title", "content"]


class ArticleSerializer(serializers.ModelSerializer[Article]):
    """Article serializer to handle returning an object."""

    class Meta:
        model = Article
        fields = "__all__"
