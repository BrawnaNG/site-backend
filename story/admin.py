from django.contrib import admin

from .models import Story, Chapter

# Register your models here.

admin.site.register(Story)
admin.site.register(Chapter)