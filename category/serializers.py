from rest_framework import serializers

from category.models import Category
from story.models import Story


class CategorySerializer(serializers.ModelSerializer):
    parent_name = serializers.SerializerMethodField()
    story_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ("name", "parent_name", "parent", "id", "description", "story_count")
        read_only_fields = ["id", "created_at", "modified_at", "user"]
        
    def get_parent_name(self, obj):
        if obj.parent:
            return obj.parent.name
        return None
    
    def get_story_count(self, obj):
        return Story.objects.filter(categories__id=obj.id).count()

class CategoryIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id")
        read_only_fields = ["id"] 
