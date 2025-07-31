from rest_framework import generics
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from accounts.permissions import IsAdmin, IsAuthor
from tag.models import Tag
from accounts.models import User
from django.db.models import Count

from .models import Story
from .serializers import (
    StorySerializer
)

from tag.serializers import TagSearchSerializer
from accounts.serializers import UserSerializer

class SearchStoryView(generics.ListAPIView):
    serializer_class = StorySerializer

    def get_queryset(self):
        query = self.request.GET.get("q")
        if query:
            queryset = Story.objects.filter(is_published = True)
            queryset = queryset.filter(
                Q(chapters__body__icontains=query)
                | Q(user__alias__icontains=query)
                | Q(brief__icontains=query)
                | Q(title__icontains=query)
            ).distinct().order_by("title")
            
        else:
            # return all stories if no search parameters are provided
            queryset = Story.objects.none()
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
class SearchAuthorView(generics.ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        user = self.request.GET.get("author")
        if user:
            queryset = User.objects.filter(alias__icontains=user).annotate(story_count=Count('story')).filter(story_count__gt=0).order_by("alias")
        else:
            # return all stories if no search parameters are provided
            queryset = User.objects.none()

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
class SearchTagView(generics.ListAPIView):
    serializer_class = TagSearchSerializer

    def get_queryset(self):
        tag = self.request.GET.get("tag")
        if tag:
            queryset = Tag.objects.filter(name__icontains=tag).order_by("name")
        else:
            # return all stories if no search parameters are provided
            queryset = Tag.objects.none()

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)   

class StoryListAdminAPIView(generics.ListAPIView):
    serializer_class = StorySerializer
    permission_class = IsAdmin

    def get_queryset(self, username):
        queryset = Story.objects.all().order_by("-created_at")
        if (username):
            queryset = queryset.filter(user__alias__icontains=username)
        return queryset
    
    def list(self, request, *args, **kwargs):
        username = self.request.GET.get("username")
        queryset = self.get_queryset(username)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class StoryListAPIView(generics.ListAPIView):
    serializer_class = StorySerializer
    queryset = Story.objects.filter(is_published=True).order_by("-created_at")
    pagination_class = PageNumberPagination
    
class StoryMineAPIView(generics.ListAPIView):
    serializer_class = StorySerializer
    permission_classes = [IsAuthor]

    def get_queryset(self, request):
        draft = self.request.GET.get("draft")
        user = request._user
        if user:
            queryset = Story.objects.filter(user__username=user.username)
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

class SavedStoriesAPIView(generics.ListAPIView):
    serializer_class = StorySerializer
    permission_classes = [IsAuthor]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        user = self.request.user
        return user.saved_stories.all()
