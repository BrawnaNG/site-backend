from django.utils.html import strip_tags
from rest_framework import serializers
import html

from category.models import Category
from category.serializers import CategorySerializer
from comment.models import Comment
from comment.serializers import CommentSerializer
from tag.models import Tag
from tag.serializers import TagSerializer

from .models import Story, Chapter

class ChapterSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.alias")
    story = serializers.ReadOnlyField(source="story.id")
    class Meta:
        model = Chapter
        fields = "__all__"
        read_only_fields = (
            "id",
            "created_at",
            "modified_date",
            "user"
        )
    
    def validate_body(self, value):
        if strip_tags(value) != value:
            raise serializers.ValidationError(
                "Chapter body should not contain HTML tags."
            )
        return value   

class StorySerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.alias")
    tags = serializers.PrimaryKeyRelatedField(many=True, read_only=False, queryset=Tag.objects.all())
    categories = serializers.PrimaryKeyRelatedField(many=True, read_only=False, queryset=Category.objects.all())

    class Meta:
        model = Story
        fields = "__all__"
        read_only_fields = (
            "id",
            "created_at",
            "slug",
            "user",
        )

class ChapterDetailSerializer(serializers.ModelSerializer):
    body = serializers.SerializerMethodField()

    class Meta:
        model = Chapter
        fields = "__all__"
        read_only_fields = (
            "id",
            "created_at",
            "modified_date",
            "user",
        )
    
    def get_body(self, obj):
        return html.unescape(obj.body)

class StoryDetailSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.alias")
    categories = CategorySerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comments = serializers.SerializerMethodField()
    chapter_ids = serializers.SerializerMethodField()

    class Meta:
        model = Story
        fields = "__all__"
        read_only_fields = (
            "created_at",
            "modified_date",
            "slug",
            "user",
        )

    def get_comments(self, obj):
        comments = Comment.objects.filter(story=obj)
        serializer = CommentSerializer(comments, many=True)
        return serializer.data
    
    def get_chapter_ids(self, obj):
        chapters = Chapter.objects.filter(story=obj)
        serializer = ChapterIdSerializer(chapters, many=True)
        return serializer.data

class ChapterIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = (
            "id",
            "modified_at"
        )
        read_only_fields = (
            "id",
            "modified_at"
        )

class StoryCreatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = "__all__"
        read_only_fields = (
            "id",
            "created_at",
            "modified_date",
            "slug",
            "user",
        )
