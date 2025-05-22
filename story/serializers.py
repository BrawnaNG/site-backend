from django.utils.html import strip_tags
from rest_framework import serializers
import html

from category.models import Category
from category.serializers import CategorySerializer
from comment.models import Comment
from comment.serializers import CommentSerializer
from tag.models import Tag
from tag.serializers import TagSerializer
from django.utils.text import slugify
from django.utils.text import Truncator

from .models import Story, Chapter, StoryChapters

class ChapterSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.alias")

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
    first_category = serializers.SerializerMethodField()
    excerpt = serializers.SerializerMethodField()

    class Meta:
        model = Story
        fields = "__all__"
        read_only_fields = (
            "id",
            "created_at",
            "slug",
            "user",
        )

    def get_first_category(self, obj):
        cat = obj.categories.first()
        if cat:
            return cat.name
        return None
    
    def get_excerpt(self, obj):
        chapter = obj.chapters.first()
        if chapter:
            chapter_body = strip_tags(html.unescape(chapter.body))
            if chapter_body and len(chapter_body) > 0:
                truncator = Truncator(chapter_body)
                return truncator.words(50,truncate="...")
        return None

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
    chapter_summaries = serializers.SerializerMethodField()

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
    
    def get_chapter_summaries(self, obj):
        ordered_chapters = obj.chapters.all().order_by('storychapters__order')
        serializer = ChapterSummarySerializer(ordered_chapters, many=True)
        return serializer.data

class ChapterSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = (
            "id",
            "modified_at",
            "title"
        )
        read_only_fields = (
            "id",
            "modified_at",
            "title"
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
        )

    def create(self, validated_data):
        title = title=validated_data["title"]
        slug = slugify(title)[:20]
        i = 1
        while Story.objects.filter(slug=slug).exists():
            slug = slugify(self.title)[:20] + "-" + str(i)
            i = i +1
        story = Story.objects.create(
            title=title,
            slug = slug,
            user=validated_data["user"],
        )
        story.save()
        return story
