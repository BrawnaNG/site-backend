from rest_framework import generics, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from accounts.permissions import IsAdmin
from tag.models import Tag
from tag.serializers import TagSerializer


class TagListAPIView(generics.ListAPIView):
    serializer_class = TagSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        query = self.request.GET.get("q")
        if query:
            queryset = Tag.objects.filter(name__icontains=query)
        else:
            queryset = Tag.objects.all()
        return queryset

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
        serializer.save(user=self.request.user)


class TagRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = "name"
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdmin]
