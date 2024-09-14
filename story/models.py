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
    body = models.TextField()
    brief = models.TextField(blank=True, null=True)
    slug = models.SlugField(unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(Tag, blank=True)
    categories = models.ManyToManyField(Category)
    chapters = models.ManyToManyField("self", blank=True, null=True, symmetrical=False)

    def save(self, *args, **kwargs):
        if strip_tags(self.body) != self.body:
            raise ValidationError("Story body should not contain HTML tags.")
        self.slug = slugify(self.body)[:20]
        if Story.objects.filter(slug=self.slug).exists():
            extra = str(randint(1, 10000000))
            self.slug = slugify(self.body)[:20] + "-" + extra
        super().save(*args, **kwargs)

    def __str__(self):
        return self.body[:20]
