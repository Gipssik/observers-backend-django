from django.db import models
from django.utils import timezone


class Notification(models.Model):
    title = models.CharField(max_length=256)
    user = models.ForeignKey(
        "authentication.User", on_delete=models.CASCADE, related_name="notifications"
    )
    question = models.ForeignKey(
        "forum.Question", on_delete=models.CASCADE, related_name="notifications"
    )

    def __str__(self):
        return self.title


class Tag(models.Model):
    title = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    title = models.CharField(max_length=256)
    content = models.TextField()
    date_created = models.DateTimeField(default=timezone.now)
    views = models.PositiveBigIntegerField(default=0)
    author = models.ForeignKey(
        "authentication.User", on_delete=models.CASCADE, related_name="questions"
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="questions")

    def __str__(self):
        return self.title


class Comment(models.Model):
    content = models.TextField()
    date_created = models.DateTimeField(default=timezone.now)
    is_answer = models.BooleanField(default=False)
    author = models.ForeignKey(
        "authentication.User", on_delete=models.CASCADE, related_name="comments"
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="comments"
    )

    def __str__(self):
        return f"{self.author.username}: {self.content[:20]}"
