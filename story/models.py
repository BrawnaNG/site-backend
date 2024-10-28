from random import randint

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.html import strip_tags
from django.utils.text import slugify

from category.models import Category
from tag.models import Tag

# Create your models here.


class Story(models.Model):
    title = models.CharField(blank=False, null=False, max_length=255)
    brief = models.TextField(blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(Tag, blank=True)
    categories = models.ManyToManyField(Category)
    is_featured = models.BooleanField(default=False)
    old_brawna_id = models.IntegerField(null=True, blank=True)
    is_published = models.BooleanField(default=False)
    has_chapters = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)[:20]
        if Story.objects.filter(slug=self.slug).exists():
            extra = str(randint(1, 10000000))
            self.slug = slugify(self.title)[:20] + "-" + extra
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Chapter(models.Model):
    title = models.CharField(blank=True, null=True, max_length=255)
    body = models.TextField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    old_brawna_id = models.IntegerField(null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    story = models.ForeignKey(Story, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if strip_tags(self.body) != self.body:
            raise ValidationError("Chapter body should not contain HTML tags.")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title    
