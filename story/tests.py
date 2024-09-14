import json
from datetime import datetime, timedelta
from unittest.mock import MagicMock

import jwt
from django.conf import settings
from django.urls import reverse
from django.utils.html import strip_tags
from rest_framework import serializers, status
from rest_framework.test import APIClient, APITestCase
from rest_framework_jwt.settings import api_settings

from accounts.models import User
from category.models import Category
from story.models import Story
from story.serializers import StoryCreatorSerializer
from tag.models import Tag


class SearchViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            alias="testuser", username="testuser", password="testpassword"
        )
        self.tag = Tag.objects.create(name="testtag")
        self.story = Story.objects.create(
            body="testbody", brief="testbrief", user=self.user
        )
        self.story.tags.add(self.tag)
        self.url = reverse("story:search")

    def test_search_by_category(self):
        response = self.client.get(self.url, {"category": "test"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_search_by_user(self):
        response = self.client.get(self.url, {"user": "testuser"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_search_by_tag(self):
        response = self.client.get(self.url, {"tag": "test"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_search_by_query(self):
        response = self.client.get(self.url, {"q": "test"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class StoryListAPIViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.url = reverse("story:story-list")

    def test_list_stories(self):
        Story.objects.create(body="testbody", brief="testbrief", user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)


class StoryCreateAPIViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword", type="Author"
        )
        self.category = Category.objects.create(name="sample_category")
        self.url = reverse("story:story-create")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_story(self):
        data = {
            "body": "testbody",
            "brief": "testbrief",
            "categories": [self.category.name],
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class StoryRetrieveUpdateDestroyAPIViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword", type="Author"
        )
        self.category = Category.objects.create(name="sample_category")
        self.story = Story.objects.create(
            body="testbody", brief="testbrief", user=self.user
        )
        self.story.categories.add(self.category)
        self.story.save()
        self.detail_url = reverse(
            "story:story-detail", kwargs={"slug": self.story.slug}
        )
        self.change_url = reverse(
            "story:story-change", kwargs={"slug": self.story.slug}
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_story(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_story(self):
        data = {"title": "newtitle", "body": "newbody", "brief": "newbrief"}
        response = self.client.patch(self.change_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_story(self):
        response = self.client.delete(self.change_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class StoryCreatorSerializerTestCase(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name="testcategories")
        self.data = {
            "body": "test body",
            "brief": "test brief",
            "user": User.objects.create_user(
                username="testuser", password="testpassword"
            ),
            "categories": [[self.category.id]],
        }
        self.serializer = StoryCreatorSerializer(data=self.data)

    def test_validate_body_with_html_tags(self):
        self.data["body"] = "<p>test body with html tags</p>"
        serializer = StoryCreatorSerializer(data=self.data)
        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_validate_body_without_html_tags(self):
        self.serializer.is_valid(raise_exception=True)
        self.assertEqual(self.serializer.validated_data["body"], "test body")
