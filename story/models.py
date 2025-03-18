from random import randint

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.html import strip_tags

from category.models import Category
from tag.models import Tag

# Create your models here.


class Story(models.Model):
    title = models.CharField(blank=False, null=False, max_length=255)
    brief = models.TextField(blank=True, default="")
    slug = models.SlugField(unique=True, blank=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(Tag, blank=True)
    categories = models.ManyToManyField(Category, blank=True)
    is_featured = models.BooleanField(default=False)
    old_brawna_id = models.IntegerField(null=True, blank=True)
    old_brawna_parent_id = models.IntegerField(null=True, blank=True)
    is_published = models.BooleanField(default=False)
    has_chapters = models.BooleanField(default=False)
        
    def __str__(self):
        return self.title

class Chapter(models.Model):
    title = models.CharField(blank=True, max_length=255, default="")
    body = models.TextField(blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    old_brawna_id = models.IntegerField(null=True, blank=True)
    old_brawna_parent_id = models.IntegerField(null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    story = models.ForeignKey(Story, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
         # If we have an old_brawna_id, it's an import, allow HTML
         # Not sure if this is a good idea!
         if strip_tags(self.body) != self.body and self.old_brawna_id == 0:
            raise ValidationError("Chapter body should not contain HTML tags.")
         super().save(*args, **kwargs)

    def __str__(self):
        if self.story:
            return f"{self.story} > {self.title}"
        return self.title
