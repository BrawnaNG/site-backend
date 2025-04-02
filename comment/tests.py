from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User
from category.models import Category
from story.models import Story

from .models import Comment
from .serializers import CommentSerializer


class CommentAPIViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.categories = Category.objects.create(name="test_category")
        self.story = Story.objects.create(
            body="Test body",
            user=User.objects.create(
                username="testuser", password="testpassword", alias="testalias"
            ),
        )
        self.story.categories.add(self.categories)
        self.comment_data = {"body": "Test comment body", "story": self.story.pk}
        self.user = User.objects.create(
            email="comment_user@gmail.ir",
            username="comment_user",
            password="password123",
            alias="comment_user",
        )
        self.client.force_authenticate(user=self.user)

    def test_list_comments(self):
        url = reverse("comment:comment-create", kwargs={"storyslug": self.story.slug})
        response = self.client.post(url, self.comment_data)

        url = reverse("comment:comment-list", kwargs={"storyslug": self.story.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        comments = Comment.objects.filter(story=self.story)
        serializer = CommentSerializer(comments, many=True)
        self.assertEqual(response.data, serializer.data)

    def test_create_comment(self):
        url = reverse("comment:comment-create", kwargs={"storyslug": self.story.slug})
        response = self.client.post(url, self.comment_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        comment = Comment.objects.get(pk=response.data["id"])
        self.assertEqual(comment.body, self.comment_data["body"])
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.story, self.story)

    def test_retrieve_comment(self):
        comment = Comment.objects.create(
            body="Test comment body", user=self.user, story=self.story
        )
        url = reverse("comment:comment-detail", kwargs={"pk": comment.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = CommentSerializer(comment)
        self.assertEqual(response.data, serializer.data)

    def test_update_comment(self):
        comment = Comment.objects.create(
            body="Test comment body", user=self.user, story=self.story
        )
        url = reverse("comment:comment-detail", kwargs={"pk": comment.pk})
        update_data = {"body": "Updated comment body"}
        response = self.client.patch(url, update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        comment.refresh_from_db()
        self.assertEqual(comment.body, update_data["body"])

    def test_delete_comment(self):
        comment = Comment.objects.create(
            body="Test comment body", user=self.user, story=self.story
        )
        url = reverse("comment:comment-detail", kwargs={"pk": comment.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(pk=comment.pk).exists())

    def test_list_admin_comments(self):
        url = reverse("comment:comment-create", kwargs={"storyslug": self.story.slug})
        response = self.client.post(url, self.comment_data)

        url = reverse("comment:comment-admin-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        admin_user = User.objects.create_user(
            username="admin",
            password="password123",
            email="admin@gmail.com",
            type="Administrator",
        )
        self.client.force_authenticate(user=admin_user)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        comments = Comment.objects.all().order_by("-created_at")
        serializer = CommentSerializer(comments, many=True)
        self.assertEqual(response.data["results"], serializer.data)

    def test_list_user_comments(self):
        url = reverse("comment:user-comment-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
