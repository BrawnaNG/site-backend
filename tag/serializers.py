from rest_framework import serializers

from story.models import Story
from .models import Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["name","id"]
        read_only_fields = ["id", "created_at", "modified_at", "user"]

class TagIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id"] 
        read_only_fields = ["id"] 

class TagSearchSerializer(serializers.ModelSerializer):
    story_count = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = ["name","id"]
        read_only_fields = ["id", "created_at", "modified_at", "user"]

    def get_story_count(self, obj):
        return Story.objects.filter(tags__icontains=obj.id).count()