from rest_framework import serializers

from news.models import Article


class ArticleBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ["title", "content"]


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = "__all__"
