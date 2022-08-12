from django.db import models
from django.utils import timezone


class Article(models.Model):
    title = models.CharField(max_length=256)
    content = models.TextField()
    date_created = models.DateTimeField(default=timezone.now)
    likes = models.ManyToManyField(
        "authentication.User", blank=True, related_name="likes"
    )
    dislikes = models.ManyToManyField(
        "authentication.User", blank=True, related_name="dislikes"
    )

    def __str__(self):
        return self.title
