from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.db.models import Count

from accounts.permissions import IsAdmin
from tag.models import Tag
from tag.serializers import TagSerializer

class CustomPagination(PageNumberPagination):
    page_size_query_param = 'page_size'
    max_page_size = 1000

class TagListAPIView(generics.ListAPIView):
    serializer_class = TagSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        query = self.request.GET.get("q")
        if query:
            return Tag.objects.filter(name__icontains=query).order_by("name")
        else:
            return Tag.objects.annotate(story_count=Count('story')).order_by("-story_count")

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TagAddAPIView(generics.CreateAPIView):
    serializer_class = TagSerializer
    permission_classes = [IsAdmin]

    def perform_create(self, serializer):
        data = self.request.data.copy()
        name = data.pop("name")
        existing_tag = Tag.objects.filter(name__iexact=name)
        if (existing_tag):
            return Response(existing_tag,status=status.HTTP_200_OK)

        serializer.save(user=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class TagUpdateView(generics.UpdateAPIView):
    lookup_field = "name"
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdmin]

class TagDestroyView(generics.DestroyAPIView):
    lookup_field = "name"
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdmin]

class TagRetrieveView(generics.RetrieveAPIView):
    lookup_field = "id"
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
