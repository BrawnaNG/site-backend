from rest_framework import serializers

from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.alias")
    story_title = serializers.ReadOnlyField(source="story.title")
    story_id = serializers.ReadOnlyField(source="story.id")

    class Meta:
        model = Comment
        fields = ["id", "body", "created_at", "user", "story_title", "story_id"]
        read_only_fields = ["created_at", "modified_at", "user"]
