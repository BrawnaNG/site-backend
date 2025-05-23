from random import randint

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.html import strip_tags

from category.models import Category
from tag.models import Tag

# Create your models here.
class Chapter(models.Model):
    title = models.CharField(blank=True, max_length=255, default="")
    body = models.TextField(blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    old_brawna_id = models.IntegerField(null=True, blank=True)
    old_brawna_parent_id = models.IntegerField(null=True, blank=True)
    is_featured = models.BooleanField(default=False)
 
    def save(self, *args, **kwargs):
         # If we have an old_brawna_id, it's an import, allow HTML
         # Not sure if this is a good idea!
         if strip_tags(self.body) != self.body and self.old_brawna_id == 0:
            raise ValidationError("Chapter body should not contain HTML tags.")
         super().save(*args, **kwargs)

    def __str__(self):
        return self.title

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
    chapters = models.ManyToManyField(
        Chapter,
        through         = 'StoryChapters',
        related_name    = 'chapters',
        verbose_name    = (u'Chapter'),
        help_text       = (u'Chapters in this Story')
    )
        
    def __str__(self):
        return self.title
    
    def chapter_list(self):
        return [sc.chapter for sc in StoryChapters.objects.filter(story=self).order_by('order')]

class StoryChapters(models.Model):
    story = models.ForeignKey(
        Story,
        verbose_name    = (u'Story'),
        help_text       = (u'Chapter is part of this Story'),
        on_delete       =  models.CASCADE
    )
    chapter = models.ForeignKey(
        Chapter,
        verbose_name    = (u'Chapter'),
        help_text       = (u'Chapter is part of this Story'),
        on_delete       =  models.CASCADE
    )
    order = models.IntegerField(
        verbose_name    = (u'Order'),
        help_text       = (u'Order of this chapter within the story')
    )

    class Meta:
        verbose_name = (u"Story Chapter")
        verbose_name_plural = (u"Story Chapters")
        ordering = ['order']
        unique_together = (('story', 'chapter'),)

    def __unicode__(self):
        return self.chapter.title + (" in position %d" % self.order) + " of " + self.story.title
