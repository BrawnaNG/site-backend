from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from accounts.models import User
from category.models import Category
from category.serializers import CategorySerializer


class CategoryListRetrieveAPIViewTestCase(APITestCase):
    def setUp(self):
        self.category_1 = Category.objects.create(name="Test category 1")
        self.category_2 = Category.objects.create(name="Test category 2")

    def test_with_list_request_returns_ok(self):
        response = self.client.get(reverse("category:category-list"))
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_with_single_category_returns_ok(self):
        url = reverse("category:category-info", args=[self.category_2.id])
        response = self.client.get(url)
        serializer = CategorySerializer(self.category_2)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_with_missing_category_returns_not_found(self):
        url = reverse("category:category-info", args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)  

class CategoryCreateAPIViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="admin", email="admin@example.com", type="administrator"
        )
        self.existing_category = Category.objects.create(name="Test category 1")
        self.client.force_authenticate(user=self.user)
        self.url = reverse("category:category-create")
        self.valid_payload = {"name": "Test category 2"}
        self.parent_category = Category.objects.create(name="Parent category 1")

    def test_with_valid_request_returns_created(self):
        response = self.client.post(self.url, self.valid_payload)
        category = Category.objects.get(name=self.valid_payload["name"])
        serializer = CategorySerializer(category)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_with_missing_name_returns_bad_request(self):
        del self.valid_payload["name"]
        response = self.client.post(self.url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) 

    def test_with_duplicate_name_returns_bad_request(self):
        self.valid_payload["name"] = self.existing_category.name
        response = self.client.post(self.url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)           

    def test_with_parent_category_returns_created(self):
        self.valid_payload["parent"] = self.parent_category.id
        response = self.client.post(self.url, self.valid_payload)
        category = Category.objects.get(name=self.valid_payload["name"])
        serializer = CategorySerializer(category)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(serializer.data["parent_name"], self.parent_category.name)

    def test_with_missing_parent_returns_bad_request(self):
        self.valid_payload["parent"] = 9999
        response = self.client.post(self.url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class CategoryUpdateAPIViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="admin", email="admin@example.com", type="administrator"
        )
        self.category = Category.objects.create(name="Test category 1")
        self.client.force_authenticate(user=self.user)
        self.update_url = reverse("category:category-edit", args=[self.category.id])

    def test_with_valid_request_returns_ok(self):
        updated_name = "Updated test category"
        response = self.client.patch(self.update_url, {"name": updated_name})
        self.category.refresh_from_db()
        serializer = CategorySerializer(self.category)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.category.name, updated_name)

    def test_with_missing_name_returns_bad_request(self):
        update_url = reverse("category:category-edit", args=[self.category.id])
        response = self.client.patch(update_url, {"name": ''})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) 

    def test_with_wrong_id_returns_not_found(self):
        update_url = reverse("category:category-edit", args=[9999])
        response = self.client.patch(update_url, {"name": 'Updated test category'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND) 

class CategoryDeletedAPIViewTestCase(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create(
            alias = "admin", 
            username="admin", 
            email="admin@example.com", 
            type="administrator"
        )
        self.author_user = User.objects.create(
            alias = "author", 
            username="author", 
            email="author@example.com", 
            type="author"
        )
        self.category = Category.objects.create(name="Test category 1")

    def test_with_valid_request_returns_deleted(self):
        self.client.force_authenticate(user=self.admin_user)
        delete_url = reverse("category:category-delete", args=[self.category.id])
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(pk=self.category.pk).exists())

    def test_with_wrong_id_returns_not_found(self):
        self.client.force_authenticate(user=self.admin_user)
        delete_url = reverse("category:category-delete", args=[9999])
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Category.objects.filter(pk=self.category.pk).exists())

    def test_with_not_admin_returns_forbidden(self):
        self.client.force_authenticate(user=self.author_user)
        delete_url = reverse("category:category-delete", args=[self.category.id])
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Category.objects.filter(pk=self.category.pk).exists()) 

    def test_with_unauthorized_returns_unauthorized(self):
        delete_url = reverse("category:category-delete", args=[self.category.id])
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Category.objects.filter(pk=self.category.pk).exists())   

