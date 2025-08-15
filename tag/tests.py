from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from tag.models import Tag


class TagListAPIViewTest(APITestCase):
    def setUp(self):
        self.tag1 = Tag.objects.create(name="test1")
        self.tag2 = Tag.objects.create(name="test2")
        self.url = reverse("tag:tag-list")

    def test_get_list_without_query(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(response.data["results"][0]["name"], self.tag1.name)
        self.assertEqual(response.data["results"][1]["name"], self.tag2.name)

    def test_get_list_with_query(self):
        response = self.client.get(self.url, {"q": "test1"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], self.tag1.name)

    def test_pagination(self):
        for i in range(24):
            Tag.objects.create(name=f"mytest{i}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 12)
