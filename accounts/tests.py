import jwt
from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User


class RegistrationAPIViewTestCase(APITestCase):
    url = reverse("accounts:registration")

    def test_registration_success(self):
        data = {
            "username": "username",
            "alias": "alias",
            "email": "testuser@example.com",
            "password": "testpassword",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("email", response.data)


class ActivationAPIViewTestCase(APITestCase):
    def test_activation_success(self):
        user = User.objects.create(
            username="test_user", alias="test_alias", email="testuser@example.com"
        )
        token = User.generate_activation_token(user.id)
        url = reverse("accounts:activation", kwargs={"token": token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("detail", response.data)
        self.assertTrue(User.objects.get(id=user.id).is_active)

    def test_activation_expired_token(self):
        token = jwt.encode(
            {"user_id": 1}, settings.SECRET_KEY, algorithm="HS256"
        ).decode("utf-8")
        url = reverse("accounts:activation", kwargs={"token": token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)

    def test_activation_invalid_token(self):
        url = reverse("accounts:activation", kwargs={"token": "invalid_token"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)


class LastUsersAPIViewTestCase(APITestCase):
    url = reverse("accounts:last_users")

    def test_last_users_list_success(self):
        user = User.objects.create(email="testuser@example.com")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("email", response.data[0])
        self.assertEqual(response.data[0]["alias"], user.alias)


class UsersListAPIViewTestCase(APITestCase):
    url = reverse("accounts:users_list")

    def test_users_list_success(self):
        user = User.objects.create(email="testuser@example.com", alias="Test User")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("email", response.data["results"][0])

    def test_users_list_search_success(self):
        user = User.objects.create(email="testuser@example.com", alias="Test User")
        response = self.client.get(self.url, {"q": "test"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("email", response.data["results"][0])
