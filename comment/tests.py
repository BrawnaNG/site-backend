from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from accounts.models import User
from category.models import Category
from story.models import Story
from tag.models import Tag

from .models import Comment
from .serializers import CommentSerializer
import json

class WithExistingStory(APITestCase):
    def setUp(self):
        self.catuser = User.objects.create_user(
            alias="catuser", 
            username="catuser", 
            password="testpassword",
            email="cats@test.com",
            type="author"
        )
        self.doguser = User.objects.create_user(
            alias="doguser", 
            username="doguser", 
            password="testpassword",
            email="dogs@test.com"
        )
        self.cattag = Tag.objects.create(name="cat")
        self.dogtag = Tag.objects.create(name="dog")
        self.catstory1 = Story.objects.create(
            title="About Cats", 
            slug="aboutcats", 
            user=self.catuser, 
            is_published=True,
            is_featured=True
        )
        self.catstory2 = Story.objects.create(
            title="More About Cats", 
            slug="moreaboutcats", 
            user=self.catuser, 
            is_published=False
        )
        self.dogstory1 = Story.objects.create(
            title="About Dogs", 
            slug="aboutdogs", 
            user=self.doguser, 
            is_published=True
        )
        self.catstory1.tags.add(self.cattag)
        self.catstory2.tags.add(self.cattag)
        self.dogstory1.tags.add(self.dogtag)
        self.category1 = Category.objects.create(name="Category 1")
        self.category2 = Category.objects.create(name="Category 2")
        self.category3 = Category.objects.create(name="Category 3")
        self.catstory1.categories.add(self.category1)
        self.catstory1.categories.add(self.category2)
        self.catstory2.categories.add(self.category1)
        self.dogstory1.categories.add(self.category3)

    def createComment(self, body, user, story) :
        return Comment.objects.create(
            body=body,
            user = user,
            story = story
        )

    def assertComments(self, story, expected_comment_ids, response_data) :
        comments = Comment.objects.filter(story=story)
        serializer = CommentSerializer(comments, many=True)
        self.assertEqual(response_data, serializer.data)
        comment_ids = list(map(lambda c: c["id"], serializer.data))
        self.assertEqual(comment_ids, expected_comment_ids)


class CommentListAPIViewTestCase(WithExistingStory):

    def setUp(self):
        super().setUp()
        self.comment1 = self.createComment("First Post!", self.catuser, self.catstory1)
        self.comment2 = self.createComment("Second Post!", self.doguser, self.catstory1)
        self.url = reverse("comment:comment-list", args=[self.catstory1.id])

    def test_with_authorized_returns_ok(self):
        self.client.force_authenticate(self.catuser)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertComments(self.catstory1, [self.comment1.id, self.comment2.id], response.data["results"])

    def test_with_not_authorized_returns_ok(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertComments(self.catstory1, [self.comment1.id, self.comment2.id], response.data["results"])

    def test_with_wrong_id_returns_bad_request(self):
        url = reverse("comment:comment-list", args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class CommentCreateAPIViewTestCase(WithExistingStory):

    def setUp(self):
        super().setUp()
        self.comment_data = {
            "body" : "First post!!"
        }
        self.url = reverse("comment:comment-create", args=[self.catstory1.id])

    def test_with_valid_request_returns_created(self):
        self.client.force_authenticate(self.catuser)
        response = self.client.post(self.url, json.dumps(self.comment_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        comment = Comment.objects.get(pk=response.data["id"])
        self.assertEqual(comment.body, self.comment_data["body"])
        self.assertEqual(comment.user, self.catuser)
        self.assertEqual(comment.story, self.catstory1)

    def test_with_not_authorized_returns_unauthorised(self):
        response = self.client.post(self.url, json.dumps(self.comment_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_with_wrong_story_id_returns_bad_request(self):
        self.client.force_authenticate(self.catuser)
        url = reverse("comment:comment-create", args=[9999])
        response = self.client.post(url, json.dumps(self.comment_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class CommentRetrieveUpdateDestroyAPIViewTestCase(WithExistingStory):

    def setUp(self):
        super().setUp()
        self.comment1 = self.createComment("First Post!", self.catuser, self.catstory1)
        self.url = reverse("comment:comment-detail", args=[self.comment1.id])
        self.bad_url = reverse("comment:comment-detail", args=[9999])
        self.comment_data = {
            "body" : "Changed my mind"
        }

    def test_with_valid_retrieve_comment_returns_ok(self):
        self.client.force_authenticate(self.catuser)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = CommentSerializer(self.comment1)
        self.assertEqual(response.data, serializer.data)

    def test_with_invalid_retrieve_comment_returns_not_found(self):
        self.client.force_authenticate(self.catuser)
        response = self.client.get(self.bad_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_with_not_authorized_retrieve_unauthorised(self):
        response = self.client.post(self.url, json.dumps(self.comment_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_with_valid_update_comment_returns_ok(self):
        self.client.force_authenticate(self.catuser)
        response = self.client.patch(self.url, json.dumps(self.comment_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.comment1.refresh_from_db()
        self.assertEqual(self.comment1.body, self.comment_data["body"])

    def test_with_invalid_update_comment_returns_not_found(self):
        self.client.force_authenticate(self.catuser)
        response = self.client.patch(self.bad_url, json.dumps(self.comment_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_with_not_authorized_update_comment_returns_unauthorized(self):
        response = self.client.patch(self.url, json.dumps(self.comment_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.comment1.refresh_from_db()
        self.assertNotEqual(self.comment1.body, self.comment_data["body"])    

    def test_with_valid_delete_comment_returns_no_content(self):
        self.client.force_authenticate(self.catuser)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(pk=self.comment1.pk).exists())

    def test_with_invalid_delete_comment_returns_not_found(self):
        self.client.force_authenticate(self.catuser)
        response = self.client.delete(self.bad_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_with_not_authorized_delete_unauthorised(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Comment.objects.filter(pk=self.comment1.pk).exists())

class CommentListAdminAPIViewTestCase(WithExistingStory):

    def setUp(self):
        super().setUp()
        self.admin_user = User.objects.create(
            username="admin", email="admin@example.com", type="administrator", alias="admin"
        )
        self.comment1 = self.createComment("First Post!", self.catuser, self.catstory1)
        self.comment2 = self.createComment("Second Post!", self.doguser, self.catstory1)
        self.comment3 = self.createComment("About dogs?!", self.catuser, self.dogstory1)
        self.url = reverse("comment:comment-admin-list")

    def assertComments(self, expected_comment_ids, response_data) :
        comments = Comment.objects.filter(id__in=expected_comment_ids).order_by("-created_at")
        serializer = CommentSerializer(comments, many=True)
        self.assertEqual(response_data, serializer.data)  

    def test_with_admin_returns_ok(self):
        self.client.force_authenticate(self.admin_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertComments([self.comment1.id, self.comment2.id, self.comment3.id], response.data["results"])

    def test_with_not_admin_returns_forbidden(self):
        self.client.force_authenticate(self.catuser)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_with_not_logged_in_returns_unauthorized(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserCommentListPIViewTestCase(WithExistingStory):

    def setUp(self):
        super().setUp()
        self.comment1 = self.createComment("First Post!", self.catuser, self.catstory1)
        self.comment2 = self.createComment("Second Post!", self.doguser, self.catstory1)
        self.comment3 = self.createComment("About dogs?!", self.catuser, self.dogstory1)
        self.url = reverse("comment:user-comment-list")

    def assertComments(self, expected_comment_ids, response_data) :
        comments = Comment.objects.filter(id__in=expected_comment_ids).order_by("-created_at")
        serializer = CommentSerializer(comments, many=True)
        self.assertEqual(response_data, serializer.data)  

    def test_with_authorized_returns_ok(self):
        self.client.force_authenticate(self.catuser)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertComments([self.comment1.id, self.comment3.id], response.data["results"])

    def test_with_not_logged_in_returns_unauthorized(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

