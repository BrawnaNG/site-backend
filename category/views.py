from rest_framework import generics

from accounts.permissions import IsAdmin
from category.models import Category
from category.serializers import CategorySerializer


class CategoryListAPIView(generics.ListAPIView):
    serializer_class = CategorySerializer
    pagination_class = None
    queryset = Category.objects.all()

class CategoryCreateAPIView(generics.CreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAdmin]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CategoryUpdateAPIView(generics.UpdateAPIView):
    lookup_field = "id"
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdmin]

class CategoryRetrieveAPIView(generics.RetrieveAPIView):
    lookup_field = "id"
    queryset = Category.objects.all()
    serializer_class = CategorySerializer