from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from accounts.models import User
from category.models import Category
from category.serializers import CategorySerializer


class CategoryListAPIViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("category:category-list")
        self.category_1 = Category.objects.create(name="Test category 1")
        self.category_2 = Category.objects.create(name="Test category 2")

    def test_get_categories(self):
        response = self.client.get(self.url)
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CategoryCreateAPIViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("category:category-create")
        self.user = User.objects.create(
            username="admin", email="admin@example.com", type="Administrator"
        )
        self.client.force_authenticate(user=self.user)
        self.valid_payload = {"name": "Test category"}

    def test_create_category(self):
        response = self.client.post(self.url, self.valid_payload)
        category = Category.objects.get(name=self.valid_payload["name"])
        serializer = CategorySerializer(category)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class CategoryRetrieveUpdateDestroyAPIViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            username="admin", email="admin@example.com", type="Administrator"
        )
        self.client.force_authenticate(user=self.user)
        self.category = Category.objects.create(name="Test category")
        self.url = reverse("category:category-detail", args=[self.category.name])

    def test_retrieve_category(self):
        response = self.client.get(self.url)
        serializer = CategorySerializer(self.category)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_category(self):
        updated_name = "Updated test category"
        response = self.client.patch(self.url, {"name": updated_name})
        self.category.refresh_from_db()
        serializer = CategorySerializer(self.category)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.category.name, updated_name)

    def test_delete_category(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(pk=self.category.pk).exists())
