import jwt
from datetime import datetime, timedelta, timezone
from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User

class RegistrationAPIViewTestCase(APITestCase):
    def setUp(self):
        self.url = reverse("accounts:registration")
        self.data = {
            "username": "username",
            "alias": "alias",
            "email": "testuser@example.com",
            "password": "testpassword",
        }

    def test_with_valid_request_returns_ok(self):
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("email", response.data)

    def test_with_missing_username_returns_bad_request(self):
        del self.data["username"]
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_with_missing_email_returns_bad_request(self):
        del self.data["email"]
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_with_missing_alias_returns_bad_request(self):
        del self.data["alias"]
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  

    def test_with_missing_password_returns_bad_request(self):
        del self.data["password"]
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  


class ActivationAPIViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="test_user", alias="test_alias", email="testuser@example.com", is_active = False
        )

    def test_with_valid_data_returns_ok(self):
        token = User.generate_activation_token(self.user.id)
        url = reverse("accounts:activation", kwargs={"token": token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("detail", response.data)
        self.assertTrue(User.objects.get(id=self.user.id).is_active)

    def test_with_expired_token_returns_bad_request(self):
        payload = {"user_id": self.user.id, "exp": datetime.now(timezone.utc) - timedelta(hours=24)}
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256").decode(
            "utf-8"
        )
        url = reverse("accounts:activation", kwargs={"token": token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("expired", response.data["detail"])
        self.assertFalse(User.objects.get(id=self.user.id).is_active)

    def test_with_invalid_token_returns_bad_request(self):
        url = reverse("accounts:activation", kwargs={"token": "invalid_token"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid", response.data["detail"])
        self.assertFalse(User.objects.get(id=self.user.id).is_active)


class LastUsersAPIViewTestCase(APITestCase):
    url = reverse("accounts:last-users")

    def test_with_valid_request_returns_okay(self):
        user = User.objects.create(email="testuser@example.com")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("email", response.data[0])
        self.assertEqual(response.data[0]["alias"], user.alias)


class UsersListAPIViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser", email="testuser@example.com", alias="Test User")
        self.url = reverse("accounts:users-list")

    def test_with_valid_request_returns_ok(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("email", response.data["results"][0])

    def test_with_query_respects_query(self):
        user2 = User.objects.create(username="catuser", email="catuser@example.com", alias="Cat User")
        response = self.client.get(self.url, {"q": "cat"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]),1)
        self.assertEqual(user2.email, response.data["results"][0]["email"])

class UserRoleListAPIView(APITestCase):
    def setUp(self):
        self.url = reverse("accounts:user-role")

    def test_with_admin_role_returns_admin(self):
        user = User.objects.create(
            username="admin", email="admin@example.com", type="administrator"
        )
        self.client.force_authenticate(user=user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual("administrator", response.data["role"])

    def test_with_author_role_returns_author(self):
        user = User.objects.create(
            username="admin", email="admin@example.com", type="author"
        )
        self.client.force_authenticate(user=user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual("author", response.data["role"])

    def test_with_reader_role_returns_reader(self):
        user = User.objects.create(
            username="admin", email="admin@example.com", type="reader"
        )
        self.client.force_authenticate(user=user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual("reader", response.data["role"])    

    def test_with_no_role_returns_reader(self):
        user = User.objects.create(username="admin", email="admin@example.com")
        self.client.force_authenticate(user=user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual("reader", response.data["role"])  

class ChangePasswordView(APITestCase):
    def setUp(self):
        self.user_email = "testuser@example.com"
        self.url = reverse("accounts:change-password",args=[self.user_email])
        self.admin_user = User.objects.create(
            username="admin", alias="admin", email="admin@example.com", type="administrator"
        )
        self.user = User.objects.create(
            username="testuser", alias="testuser", email=self.user_email, type="reader"
        )

    def test_with_admin_returns_ok(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            "password": "testpassword",
            "confirm_password": "testpassword",
        }
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual("password set", response.data["status"])

    def test_with_non_admin_returns_forbidden(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "password": "testpassword",
            "confirm_password": "testpassword",
        }
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)