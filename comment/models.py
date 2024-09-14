from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from story.models import Story

User = get_user_model()


class Comment(models.Model):
    body = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    story = models.ForeignKey(Story, on_delete=models.CASCADE)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.user.username}'s comment on {self.story.slug}"
