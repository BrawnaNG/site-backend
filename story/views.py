from rest_framework import generics
from django.db.models import Q
from django.forms.models import model_to_dict
from rest_framework import generics, permissions, status
from rest_framework.exceptions import (
    NotFound,
    ValidationError
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import (
    APIView,
)
from accounts.permissions import IsAdmin, IsAuth, IsAuthor
from category.models import Category
from tag.models import Tag
import html

from .models import Story, Chapter
from .serializers import (
    StorySerializer,
    StoryDetailSerializer,
    StoryCreatorSerializer,
    ChapterSerializer,
    ChapterDetailSerializer
)

class SearchView(generics.ListAPIView):
    serializer_class = StorySerializer

    def get_queryset(self):
        query = self.request.GET.get("q")
        category = self.request.GET.get("category")
        user = self.request.GET.get("user")
        tag = self.request.GET.get("tag")

        if category:
            queryset = Story.objects.filter(categories__name__icontains=category)
        elif user:
            queryset = Story.objects.filter(user__alias__icontains=user)
        elif tag:
            queryset = Story.objects.filter(tags__name__icontains=tag)
        elif query:
            queryset = Story.objects.filter(
                Q(body__icontains=query)
                | Q(brief__icontains=query)
                | Q(user__alias__icontains=query)
            )
        else:
            # return all stories if no search parameters are provided
            queryset = Story.objects.none()

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class StoryListAPIView(generics.ListAPIView):
    serializer_class = StorySerializer

    def get_queryset(self):
        queryset = Story.objects.all().order_by("-created_at")
        queryset = queryset.filter(is_published=True)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
class StoryMineAPIView(generics.ListAPIView):
    serializer_class = StorySerializer
    permission_classes = [IsAuthor]

    def get_queryset(self, request):
        draft = self.request.GET.get("draft")
        user = request._user
        if user:
            queryset = Story.objects.all()
            queryset = queryset.filter(user__username=user.username)
            if draft and draft == "1":
                queryset = queryset.filter(is_published=False)
            else:
                queryset = queryset.filter(is_published=True)
            return queryset.order_by("-created_at")
        else:
            return None
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset(request)
        if queryset is None:
            return Response([])
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class StoryFeaturedAPIView(generics.RetrieveAPIView):
    serializer_class = StorySerializer
    permission_classes = []

    def get_queryset(self):
        return Story.objects.all().filter(is_featured=True).order_by("-created_at")[:1]

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class StoryRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = "id"
    queryset = Story.objects.all()
    serializer_class = StorySerializer
    permission_classes = [IsAuthor]

class StoryDetailAPIView(generics.RetrieveAPIView):
    lookup_field = "id"
    queryset = Story.objects.all()
    serializer_class = StoryDetailSerializer
    permission_classes = []

class ChapterDetailAPIView(generics.RetrieveAPIView):
    lookup_field = "id"
    queryset = Chapter.objects.all()
    serializer_class = ChapterDetailSerializer
    permission_classes = []

class SavedStoriesAPIView(generics.ListAPIView):
    serializer_class = StorySerializer
    permission_classes = [IsAuthor]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        user = self.request.user
        return user.saved_stories.all()

class ChapterCreateAPIView(generics.CreateAPIView):
    serializer_class = ChapterSerializer
    permission_classes = [IsAuthor]

    def perform_create(self, serializer):
        try:
            story_id = self.kwargs["storyid"]
            story = Story.objects.get(id=story_id)
            if serializer.is_valid():
                serializer.save(user=self.request.user, story=story)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Story.DoesNotExist:
            raise ValidationError("Invalid story id provided.")
        except KeyError:
            raise ValidationError("Story id is missing from URL.")

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data["body"] = html.escape(data.pop("body"))
        serializer = self.get_serializer(data=data)
        self.perform_create(serializer)
        return Response(
            data="Chapter created successfully.", status=status.HTTP_201_CREATED
        )

class SaveChapterAPIView(generics.UpdateAPIView):
    serializer_class = ChapterSerializer
    permission_classes = [IsAuthor]
    queryset = Chapter.objects.all()
    lookup_field = "id"

    def get_object(self):
        return self.queryset.get(id=self.kwargs.get("id"))
    
    def put(self, request, *args, **kwargs):
        chapter = self.get_object()
        data = request.data.copy()
        data["body"] = html.escape(data.pop("body"))
        serializer = self.get_serializer(data=data)

        if serializer.is_valid():
            title = serializer.validated_data["title"]
            body = serializer.validated_data["body"]
            chapter.title = title
            chapter.body = body
            chapter.save()
            return Response({"status": "chapter saved"})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StoryCreateAPIView(generics.CreateAPIView):
    serializer_class = StoryCreatorSerializer
    permission_classes = [IsAuthor]

    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        serializer.create(user = self.request.user)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        serializer = self.get_serializer(data=data)
        self.perform_create(serializer)
        return Response(serializer.data)

class SaveStoryAPIView(generics.UpdateAPIView):
    serializer_class = StorySerializer
    permission_classes = [IsAuthor]
    queryset = Story.objects.all()
    lookup_field = "id"

    def get_object(self):
        return self.queryset.get(id=self.kwargs.get("id"))

    def put(self, request, *args, **kwargs):
        story = self.get_object()
        data = request.data.copy()

        tag_names = data.pop("tags", [])
        if tag_names:
            tag_names = tag_names[0].split(",")
            tag_ids = Tag.objects.filter(name__in=tag_names).values_list(
                "id", flat=True
            )
            if len(tag_names) != len(tag_ids):
                raise NotFound("Tag not found!")
            data["tags"] = list(tag_ids)
        else:
            data["tags"] = []

        category_names = data.pop("categories", [])
        if category_names:
            category_names = category_names[0].split(",")
            category_ids = Category.objects.filter(name__in=category_names).values_list(
                "id", flat=True
            )
            if len(category_names) != len(category_ids):
                raise NotFound("Category not found!")
            data["categories"] = list(category_ids)
        else:
            data["categories"] = []

        serializer = self.get_serializer(data=data)

        if serializer.is_valid():
            title = serializer.validated_data["title"]
            is_published = serializer.validated_data["is_published"]
            has_chapters = serializer.validated_data["has_chapters"]
            tags = serializer.validated_data["tags"]
            categories = serializer.validated_data["categories"]
            story.title = title
            story.is_published = is_published
            story.has_chapters = has_chapters
            story.tags.set(tags)
            story.categories.set(categories)
            story.save()
            return Response({"status": "story saved"})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class DeleteSavedStoryAPIView(generics.DestroyAPIView):
    serializer_class = StorySerializer
    permission_classes = [IsAuth]

    def delete(self, request, *args, **kwargs):
        user = request.user
        story_id = self.kwargs.get("id")
        try:
            story = user.saved_stories.get(id=story_id)
        except Story.DoesNotExist:
            raise NotFound("Story not found in saved stories!")

        user.saved_stories.remove(story)
        return Response({"detail": "Story removed from saved stories successfully."})
