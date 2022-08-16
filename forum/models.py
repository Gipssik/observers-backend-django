from django.db import models
from django.utils import timezone


class Tag(models.Model):
    """Model for database table 'tag'."""

    title = models.CharField(max_length=64, unique=True)

    def __str__(self) -> str:
        return self.title


class Question(models.Model):
    """Model for database table 'question'."""

    title = models.CharField(max_length=256)
    content = models.TextField()
    date_created = models.DateTimeField(default=timezone.now)
    views = models.PositiveBigIntegerField(default=0)
    author = models.ForeignKey(
        "authentication.User",
        on_delete=models.CASCADE,
        related_name="questions",
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="questions")

    def __str__(self) -> str:
        return self.title


class Comment(models.Model):
    """Model for database table 'comment'."""

    content = models.TextField()
    date_created = models.DateTimeField(default=timezone.now)
    is_answer = models.BooleanField(default=False)
    author = models.ForeignKey(
        "authentication.User",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="comments",
    )

    def __str__(self) -> str:
        username = self.author.username
        content = self.content[:20]
        return f"{username}: {content}"
