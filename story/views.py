from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdmin, IsAuth, IsAuthor
from category.models import Category
from tag.models import Tag

from .models import Story
from .serializers import StoryCreatorSerializer, StoryDetailSerializer, StorySerializer


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
    pagination_class = PageNumberPagination

    def get_queryset(self):
        queryset = Story.objects.all()
        username = self.request.query_params.get("username")
        if username:
            queryset = queryset.filter(user__username=username)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class StoryCreateAPIView(generics.CreateAPIView):
    serializer_class = StoryCreatorSerializer
    permission_classes = [IsAuthor]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        # category
        category_names = data.pop("categories", [])[0].split(",")
        category_ids = Category.objects.filter(name__in=category_names).values_list(
            "id", flat=True
        )
        if len(category_names) != len(category_ids):
            raise NotFound("Category not found!")
        data["categories"] = list(category_ids)

        # tag
        tag_names = data.pop("tags", [])
        if tag_names:
            tag_names = tag_names[0].split(",")
            tag_ids = Tag.objects.filter(name__in=tag_names).values_list(
                "id", flat=True
            )
            if len(tag_names) != len(tag_ids):
                raise NotFound("Tag not found!")
            data["tags"] = list(tag_ids)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            data="Story created successfully.", status=status.HTTP_201_CREATED
        )


class StoryRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = "slug"
    queryset = Story.objects.all()
    serializer_class = StorySerializer
    permission_classes = [IsAuthor]


class StoryDetailAPIView(generics.RetrieveAPIView):
    lookup_field = "slug"
    queryset = Story.objects.all()
    serializer_class = StoryDetailSerializer
    permission_classes = []


class SavedStoriesAPIView(generics.ListAPIView):
    serializer_class = StorySerializer
    permission_classes = [IsAuth]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        user = self.request.user
        return user.saved_stories.all()


class CreateSaveStoryAPIView(APIView):
    permission_classes = [IsAuth]

    def post(self, request, story_slug, *args, **kwargs):
        user = request.user
        try:
            story = Story.objects.get(slug=story_slug)
        except Story.DoesNotExist:
            raise NotFound("Story not found!")

        user.saved_stories.add(story)
        return Response({"detail": "Story saved successfully."})


class DeleteSavedStoryAPIView(generics.DestroyAPIView):
    serializer_class = StorySerializer
    permission_classes = [IsAuth]

    def delete(self, request, *args, **kwargs):
        user = request.user
        story_id = self.kwargs.get("story_slug")
        try:
            story = user.saved_stories.get(slug=story_id)
        except Story.DoesNotExist:
            raise NotFound("Story not found in saved stories!")

        user.saved_stories.remove(story)
        return Response({"detail": "Story removed from saved stories successfully."})
