from django.contrib import admin

from .models import Story, StoryChapters, Chapter

# Register your models here.

from django.contrib import admin
class StoryChaptersInline(admin.TabularInline):
    model = StoryChapters
    extra = 1    

class StoryAdmin(admin.ModelAdmin):
    inlines = [StoryChaptersInline]

admin.site.register(Story, StoryAdmin)
admin.site.register(Chapter)