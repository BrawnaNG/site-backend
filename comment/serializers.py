from rest_framework import serializers

from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.alias")
    story = serializers.ReadOnlyField(source="story.title")

    class Meta:
        model = Comment
        fields = ["id", "body", "created_at", "user", "story"]
        read_only_fields = ["created_at", "modified_at", "user"]
