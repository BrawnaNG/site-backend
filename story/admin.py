from django.contrib import admin

from .models import Story, Chapter

# Register your models here.

from django.contrib import admin
class ChapterInline(admin.TabularInline):
    model = Chapter
    fk_name = 'story'

class StoryAdmin(admin.ModelAdmin):
    inlines = [
        ChapterInline,
    ]

admin.site.register(Story, StoryAdmin)
admin.site.register(Chapter)
