from django.db import models
from django.utils import timezone


class Article(models.Model):
    """Model for database table 'article'."""

    class Meta:
        ordering = ["-date_created"]

    title = models.CharField(max_length=256)
    content = models.TextField()
    date_created = models.DateTimeField(default=timezone.now)
    likes = models.ManyToManyField(
        "authentication.User",
        blank=True,
        related_name="likes",
    )
    dislikes = models.ManyToManyField(
        "authentication.User",
        blank=True,
        related_name="dislikes",
    )

    def __str__(self) -> str:
        return self.title
