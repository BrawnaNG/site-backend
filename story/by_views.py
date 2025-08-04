from rest_framework import generics
from rest_framework.response import Response

from .models import Story
from .serializers import StorySerializer
    
class ByCategoryView(generics.ListAPIView):
    serializer_class = StorySerializer

    def get_queryset(self):
        category_id = self.kwargs["id"]
        if category_id:
            queryset = Story.objects.filter(is_published=True).filter(categories__id=category_id).order_by("-created_at")
        else:
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
    
class ByTagView(generics.ListAPIView):
    serializer_class = StorySerializer

    def get_queryset(self):
        tag_id = self.kwargs["id"]
        if tag_id:
            queryset = Story.objects.filter(is_published=True).filter(tags__id=tag_id).order_by("-created_at")
        else:
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

class ByAuthorView(generics.ListAPIView):
    serializer_class = StorySerializer

    def get_queryset(self):
        author_id = self.kwargs["id"]
        if author_id:
            queryset = Story.objects.filter(is_published=True).filter(user__id=author_id).order_by("-created_at")
        else:
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
