
from datetime import datetime, timedelta
from unittest.mock import MagicMock
import json

from django.conf import settings
from django.urls import reverse
from django.utils.html import strip_tags
from rest_framework import serializers, status
from rest_framework.test import APIClient, APITestCase
from rest_framework_jwt.settings import api_settings

from accounts.models import User
from category.models import Category
from story.models import Story, Chapter, StoryChapters
from story.serializers import (
    StoryCreatorSerializer,
    StorySerializer,
    StoryDetailSerializer,
    ChapterDetailSerializer,
    ChapterSerializer,
    ChapterSummarySerializer
)
from accounts.serializers import (
    UserSearchSerializer,
    UserSavedStoriesSerializer
)
from tag.models import Tag
from tag.serializers import TagSearchSerializer

class ExistingStoryTestCase(APITestCase):
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

    def assertSavedStoriesEquals(self, user, stories):
        serializer = UserSavedStoriesSerializer(user)
        check = { "id" : user.id, "saved_stories": list(map(lambda s: s.id, stories)) }
        self.assertEqual(check, serializer.data)        

class StoryRetrieveUpdateDestroyAPIViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword", type="author")
        self.category = Category.objects.create(name="sample_category")
        self.story = Story.objects.create(
            title="testtitle", user=self.user)
        self.story.categories.add(self.category)
        self.story.save()  
        self.url = reverse(
            "story:story-change", args=[self.story.id])
        self.bad_url = reverse(
            "story:story-change", args=[9999]) 
        self.client.force_authenticate(user=self.user)

    def test_retrieve_with_valid_request_returns_ok(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = StorySerializer(self.story)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_with_wrong_id_returns_not_found(self):
        response = self.client.get(self.bad_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_with_valid_request_returns_ok(self):
        data = {"title": "newtitle"}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.story.refresh_from_db()
        serializer = StorySerializer(self.story)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(self.story.title, "newtitle")

    def test_update_with_wrong_id_returns_not_found(self):
        data = {"title": "newtitle"}
        response = self.client.patch(self.bad_url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.story.refresh_from_db()
        self.assertEqual(self.story.title, "testtitle")

    def test_update_with_missing_title_returns_bad_request(self):
        data = {"title": ""}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.story.refresh_from_db()
        self.assertEqual(self.story.title, "testtitle")

    def test_delete_with_valid_request_returns_deleted(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Story.objects.filter(pk=self.story.pk).exists())

    def test_delete_with_wrong_id_returns_not_dound(self):
        response = self.client.delete(self.bad_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Story.objects.filter(pk=self.story.pk).exists())   

class StoryCreateAPIViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword", type="author"
        )
        self.url = reverse("story:story-create")
        self.client.force_authenticate(user=self.user)

    def test_with_valid_data_returns_created(self):
        data = {
            "title": "testtitle"
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        story = Story.objects.get(id=response.data["id"])
        self.assertEqual(story.title, data["title"])
        self.assertEqual(story.user, self.user)

    def test_with_missing_title_returns_bad_request(self):
        data = {
            "title": ""
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)   

class StorySaveAPIViewTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            alias="testuser", 
            email ="testuser@example.com", 
            username="testuser", 
            password="testpassword", 
            type="author")
        self.user2 = User.objects.create_user(
            alias="testuser2", 
            email ="testuser2@example.com", 
            username="testuser2", 
            password="testpassword", 
            type="author")
        self.category = Category.objects.create(name="sample_category")
        self.cattag = Tag.objects.create(name="cat")
        self.dogtag = Tag.objects.create(name="dog")
        self.story = Story.objects.create(
            title="testtitle", user=self.user1)
        self.url = reverse(
            "story:story-save", args=[self.story.id])
        self.bad_url = reverse(
            "story:story-save", args=[9999]) 
        self.client.force_authenticate(user=self.user1)
        pigtag = { "name": "pig"}
        cattag = { "id" : self.cattag.id }

        tags = [ 
                cattag, 
                pigtag
        ]
        categories = [{"id":self.category.id}]
        self.valid_data = {
            "title": "newtitle",
            "tags": tags,
            "categories": categories,
            "is_published": True,
            "has_chapters": True,
        }

    def assertStoryUnchanged(self):
        self.story.refresh_from_db()
        serializer = StorySerializer(self.story)
        self.assertEqual("testtitle",self.story.title)
        self.assertFalse(self.story.is_published)
        self.assertFalse(self.story.has_chapters)
        tags = []
        categories = []
        self.assertSequenceEqual(tags, serializer.data["tags"])
        self.assertSequenceEqual(categories, serializer.data["categories"])

    def test_with_valid_request_returns_ok(self):
        response = self.client.put(self.url, data=json.dumps(self.valid_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.story.refresh_from_db()
        serializer = StorySerializer(self.story)
        self.assertEqual(self.valid_data["title"],self.story.title)
        self.assertTrue(self.story.is_published)
        self.assertTrue(self.story.has_chapters)
        pigtag = Tag.objects.get(name="pig")
        tags = [self.cattag.id,pigtag.id]
        categories = [self.category.id]
        self.assertSequenceEqual(tags, serializer.data["tags"])
        self.assertSequenceEqual(categories, serializer.data["categories"])

    def test_with_invalid_request_returns_bad_request(self):
        self.valid_data["title"] = ""
        response = self.client.put(self.url, data=json.dumps(self.valid_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertStoryUnchanged();
    
    def test_with_wrong_user_returns_forbidden(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.put(self.bad_url, data=json.dumps(self.valid_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertStoryUnchanged    

#forbidden rather than not found because the IsOwnerOrAdmin permission is stepping in
    def test_with_wrong_id_returns_forbidden(self):
        response = self.client.put(self.bad_url, data=json.dumps(self.valid_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertStoryUnchanged
    
class StoryDetailAPIViewTestCase(ExistingStoryTestCase):
    def test_with_valid_request_returns_ok(self):
        url = reverse("story:story-detail", args=[self.catstory1.id])
        response = self.client.get(url)
        serializer = StoryDetailSerializer(self.catstory1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_with_wrong_id_request_returns_not_found(self):
        bad_url = reverse("story:story-detail", args=[9999])
        response = self.client.get(bad_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class StoryCheckAuthorAPIView(ExistingStoryTestCase):
    def test_when_is_author_returns_ok(self):
        self.client.force_authenticate(user=self.catuser)
        url = reverse("story:story-check-author", args=[self.catstory1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data)

    def test_when_is_not_author_returns_ok(self):
        self.client.force_authenticate(user=self.doguser)
        url = reverse("story:story-check-author", args=[self.catstory1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data)

    def test_with_bad_id_request_returns_not_found(self):
        self.client.force_authenticate(user=self.catuser)
        url = reverse("story:story-check-author", args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_with_not_authenticated_returns_unauthorized(self):
        url = reverse("story:story-check-author", args=[self.catstory1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AddSavedStoryAPIViewTest(ExistingStoryTestCase):
    def test_with_valid_request_returns_ok(self):
        self.catuser.saved_stories.add(self.dogstory1)
        self.doguser.saved_stories.add(self.dogstory1)
        self.client.force_authenticate(user=self.catuser)
        url = reverse("story:story-saved-add", args=[self.catstory1.id])
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.catuser.refresh_from_db()
        self.doguser.refresh_from_db()
        self.assertSavedStoriesEquals(self.catuser, [self.catstory1, self.dogstory1, ])
        self.assertSavedStoriesEquals(self.doguser, [self.dogstory1])

    def test_with_bad_id_request_returns_not_found(self):
        self.doguser.saved_stories.add(self.dogstory1)
        self.client.force_authenticate(user=self.catuser)
        url = reverse("story:story-saved-add", args=[9999])
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.catuser.refresh_from_db()
        self.doguser.refresh_from_db()
        self.assertSavedStoriesEquals(self.catuser, [])
        self.assertSavedStoriesEquals(self.doguser, [self.dogstory1])

    def test_with_not_authenticated_returns_unauthorized(self):
        self.catuser.saved_stories.add(self.catstory1)
        url = reverse("story:story-saved-add", args=[self.dogstory1.id])
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertSavedStoriesEquals(self.catuser, [self.catstory1])  

class DeleteSavedStoryAPIViewTest(ExistingStoryTestCase):
    def test_with_valid_request_returns_ok(self):
        self.catuser.saved_stories.add(self.catstory1)
        self.catuser.saved_stories.add(self.dogstory1)
        self.doguser.saved_stories.add(self.dogstory1)
        self.client.force_authenticate(user=self.catuser)
        url = reverse("story:story-saved-delete", args=[self.dogstory1.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.catuser.refresh_from_db()
        self.doguser.refresh_from_db()
        self.assertSavedStoriesEquals(self.catuser, [self.catstory1])
        self.assertSavedStoriesEquals(self.doguser, [self.dogstory1])

    def test_with_bad_id_request_returns_not_found(self):
        self.catuser.saved_stories.add(self.catstory1)
        self.client.force_authenticate(user=self.catuser)
        url = reverse("story:story-saved-delete", args=[9999])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertSavedStoriesEquals(self.catuser, [self.catstory1])

    def test_with_wrong_story_request_returns_not_found(self):
        self.catuser.saved_stories.add(self.catstory1)
        self.client.force_authenticate(user=self.catuser)
        url = reverse("story:story-saved-delete", args=[self.dogstory1.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertSavedStoriesEquals(self.catuser, [self.catstory1])
        
    def test_with_not_authenticated_returns_unauthorized(self):
        self.catuser.saved_stories.add(self.catstory1)
        url = reverse("story:story-saved-delete", args=[self.catstory1.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertSavedStoriesEquals(self.catuser, [self.catstory1])

class SavedStoriesAPIView(ExistingStoryTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("story:story-saved-list")

    def assertSavedStoriesEquals(self, check, stories):
        serializer = StorySerializer(stories, many=True)
        self.assertEqual(check, serializer.data)   

    def test_with_valid_request_returns_ok(self):
        self.catuser.type = "reader"
        self.catuser.saved_stories.add(self.catstory1)
        self.catuser.saved_stories.add(self.dogstory1)
        self.catuser.save()
        self.catuser.refresh_from_db()
        self.client.force_authenticate(user=self.catuser)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertSavedStoriesEquals(response.data["results"], [self.dogstory1, self.catstory1])

    def test_with_not_authenticated_returns_unauthorized(self):
        self.catuser.saved_stories.add(self.catstory1)
        self.catuser.saved_stories.add(self.dogstory1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class ChapterDetailAPIView(ExistingStoryTestCase):
    def setUp(self):
        super().setUp()
        chapter_data = {
            "title": "Chapter One",
            "body" : "It was a dark and stormy night"
        }
        serializer = ChapterSerializer(data=chapter_data)
        if serializer.is_valid():
            serializer.save(user=self.catuser)
            StoryChapters.objects.create(story=self.catstory1,chapter=serializer.instance,order=0)
            self.chapter1 = serializer.instance
            self.url = reverse("story:chapter-detail", args = [self.chapter1.id])

    def test_with_valid_request_returns_ok(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = ChapterDetailSerializer(self.chapter1)
        self.assertEqual(serializer.data, response.data)

    def test_with_wrong_id_returns_not_found(self):
        self.url = reverse("story:chapter-detail", args = [9999])
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class ChapterTestCase(ExistingStoryTestCase):
    def setUp(self):
        super().setUp()
        self.chapter1_data = {
            "title": "Chapter One",
            "pos" : 0,
            "body" : ""
        }
        self.chapter2_data = {
            "title": "Chapter Two",
            "pos" : 1,
            "body" : ""
        }
        self.chapter3_data = {
            "title": "Chapter Three",
            "pos" : 2,
            "body" : ""
        }

    def addChapter(self, story, data, pos, user):
        serializer = ChapterSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=user)
            StoryChapters.objects.create(story=story,chapter=serializer.instance,order=pos)
        return serializer.instance
    
    def assertStoryChapters(self, story, expected_chapter_ids):
        serializer = StoryDetailSerializer(story)
        chapter_ids = list(map(lambda c: c["id"], serializer.data["chapter_summaries"]))
        self.assertEqual(chapter_ids, expected_chapter_ids)
        pos = 0
        for id in chapter_ids:
            chapter = Chapter.objects.get(id=id)
            story_chapter = StoryChapters.objects.get(chapter=chapter)
            self.assertEqual(story_chapter.order, pos)
            pos+=1

class ChapterCreateAPIView(ChapterTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("story:chapter-create", kwargs = {"storyid":self.catstory1.id})

    def assertChapter(self, chapter_id, response_data, test_data):
        chapter = Chapter.objects.get(id=chapter_id)
        serializer = ChapterSerializer(chapter)
        self.assertEqual(serializer.data, response_data)
        self.assertEqual(chapter.title, test_data["title"])
        story_chapter = StoryChapters.objects.get(chapter=chapter)
        self.assertEqual(story_chapter.order,test_data["pos"])

    def test_with_add_chapter_after_returns_created(self):
        chapter1 = self.addChapter(self.catstory1, self.chapter1_data, 0, self.catuser)
        self.client.force_authenticate(user=self.catuser)
        response = self.client.post(self.url, data=json.dumps(self.chapter2_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.catstory1.refresh_from_db()
        id = response.data["id"]
        self.assertChapter(id, response.data, self.chapter2_data)
        self.assertStoryChapters(self.catstory1, [chapter1.id, id])

    def test_with_add_chapter_before_returns_created(self):
        chapter2 = self.addChapter(self.catstory1, self.chapter2_data, 0, self.catuser)
        self.client.force_authenticate(user=self.catuser)
        response = self.client.post(self.url, data=json.dumps(self.chapter1_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.catstory1.refresh_from_db()
        id = response.data["id"]
        self.assertChapter(id, response.data, self.chapter1_data)
        self.assertStoryChapters(self.catstory1, [id, chapter2.id])

    def test_with_add_chapter_between_returns_created(self):
        chapter1 = self.addChapter(self.catstory1, self.chapter1_data, 0, self.catuser)
        chapter3 = self.addChapter(self.catstory1, self.chapter3_data, 1, self.catuser)
        self.client.force_authenticate(user=self.catuser)
        response = self.client.post(self.url, data=json.dumps(self.chapter2_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.catstory1.refresh_from_db()
        id = response.data["id"]
        self.assertChapter(id, response.data, self.chapter2_data)
        self.assertStoryChapters(self.catstory1, [chapter1.id, id, chapter3.id])       

    def test_with_first_returns_created(self):
        self.client.force_authenticate(user=self.catuser)
        response = self.client.post(self.url, data=json.dumps(self.chapter1_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.catstory1.refresh_from_db()
        id = response.data["id"]
        self.assertChapter(id, response.data, self.chapter1_data)
        self.assertStoryChapters(self.catstory1, [id])

    #The IsOwnerOrAdmin permission kicks in to return forbidden
    def test_with_wrong_story_id_returns_forbidden(self):
        self.client.force_authenticate(user=self.catuser)
        self.url = reverse("story:chapter-create", kwargs = {"storyid":9999})                                
        response = self.client.post(self.url, data=json.dumps(self.chapter1_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_with_wrong_author_returns_forbidden(self):
        self.client.force_authenticate(user=self.doguser)
        response = self.client.post(self.url, data=json.dumps(self.chapter1_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_with_not_authorized_returns_unauthorized(self):
        response = self.client.post(self.url, data=json.dumps(self.chapter1_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)    

class ChapterSaveAPIView(ChapterTestCase):
    def setUp(self):
        super().setUp()
        self.chapter1 = self.addChapter(self.catstory1, self.chapter1_data, 0, self.catuser)
        self.url = reverse("story:chapter-save", args = [self.catstory1.id, self.chapter1.id])
        self.chapter1_data["body"] = "It was a dark and stormy night"
        self.chapter1_data["title"] = "Chapter the first"

    def assertChapter(self, chapter_id, test_data):
        chapter = Chapter.objects.get(id=chapter_id)
        self.assertEqual(chapter.title, test_data["title"])
        story_chapter = StoryChapters.objects.get(chapter=chapter)
        story_chapter.pos = test_data["pos"]
        self.assertEqual(chapter.body, test_data["body"])

    def test_with_valid_request_returns_ok(self):
        self.client.force_authenticate(user=self.catuser)
        response = self.client.put(self.url, data=json.dumps(self.chapter1_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.catstory1.refresh_from_db()
        self.assertChapter(self.chapter1.id, self.chapter1_data)
        self.assertStoryChapters(self.catstory1, [self.chapter1.id])

    #The IsOwnerOrAdmin permission kicks in to return forbidden
    def test_with_wrong_story_id_returns_forbidden(self):
        self.client.force_authenticate(user=self.catuser)
        self.url = reverse("story:chapter-save", args = [9999, self.chapter1.id])                               
        response = self.client.put(self.url, data=json.dumps(self.chapter1_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_with_wrong_chapter_id_returns_not_found(self):
        self.client.force_authenticate(user=self.catuser)
        self.url = reverse("story:chapter-save", args = [self.catstory1.id, 9999])                               
        response = self.client.put(self.url, data=json.dumps(self.chapter1_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)    

    def test_with_wrong_author_returns_forbidden(self):
        self.client.force_authenticate(user=self.doguser)
        response = self.client.put(self.url, data=json.dumps(self.chapter1_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_with_not_authorized_returns_unauthorized(self):
        response = self.client.put(self.url, data=json.dumps(self.chapter1_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)            

class ChapterDeleteAPIView(ChapterTestCase):
    def setUp(self):
        super().setUp()
        self.chapter1 = self.addChapter(self.catstory1, self.chapter1_data, 0, self.catuser)
        self.chapter2 = self.addChapter(self.catstory1, self.chapter2_data, 1, self.catuser)
        self.chapter3 = self.addChapter(self.catstory1, self.chapter3_data, 2, self.catuser)
        
    def test_with_delete_chapter_at_start_returns_ok(self):
        self.url = reverse("story:chapter-delete", args = [self.catstory1.id, self.chapter1.id])
        self.client.force_authenticate(user=self.catuser)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.catstory1.refresh_from_db()
        self.assertStoryChapters(self.catstory1, [self.chapter2.id, self.chapter3.id])

    def test_with_delete_chapter_at_end_returns_ok(self):
        self.url = reverse("story:chapter-delete", args = [self.catstory1.id, self.chapter3.id])
        self.client.force_authenticate(user=self.catuser)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.catstory1.refresh_from_db()
        self.assertStoryChapters(self.catstory1, [self.chapter1.id, self.chapter2.id])

    def test_with_delete_chapter_in_middle_returns_ok(self):
        self.url = reverse("story:chapter-delete", args = [self.catstory1.id, self.chapter2.id])
        self.client.force_authenticate(user=self.catuser)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.catstory1.refresh_from_db()
        self.assertStoryChapters(self.catstory1, [self.chapter1.id, self.chapter3.id]) 

     #The IsOwnerOrAdmin permission kicks in to return forbidden
    def test_with_wrong_story_id_returns_forbidden(self):
        self.client.force_authenticate(user=self.catuser)
        self.url = reverse("story:chapter-delete", args = [9999, self.chapter2.id])                             
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_with_wrong_chapter_id_returns_not_found(self):
        self.client.force_authenticate(user=self.catuser)
        self.url = reverse("story:chapter-delete", args = [self.catstory1.id, 9999])                             
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)    

    def test_with_wrong_author_returns_forbidden(self):
        self.url = reverse("story:chapter-delete", args = [self.catstory1.id, self.chapter1.id])
        self.client.force_authenticate(user=self.doguser)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_with_not_authorized_returns_unauthorized(self):
        self.url = reverse("story:chapter-delete", args = [self.catstory1.id, self.chapter1.id])
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)             


#Search test cases 
class SearchStoryViewTestCase(ExistingStoryTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("story:search-story")

    def test_when_expecting_results_get_results(self):
        response = self.client.get(self.url, {"q": "cat"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        serializer = StorySerializer(self.catstory1)
        self.assertEqual(response.data["results"][0], serializer.data)

    def test_when_not_expecting_results_get_no_results(self):
        response = self.client.get(self.url, {"q": "pig"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)        

class SearchAuthorViewTestCase(ExistingStoryTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("story:search-author")

    def test_when_expecting_results_get_results(self):
        response = self.client.get(self.url, {"author": "dog"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        serializer = UserSearchSerializer(self.doguser)
        self.assertEqual(response.data["results"][0], serializer.data)

    def test_when_not_expecting_results_get_no_results(self):
        response = self.client.get(self.url, {"author": "pig"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)     

class SearchTagViewTestCase(ExistingStoryTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("story:search-tag")

    def test_when_expecting_results_get_results(self):
        response = self.client.get(self.url, {"tag": "cat"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        serializer = TagSearchSerializer(self.cattag)
        self.assertEqual(response.data["results"][0], serializer.data)

    def test_when_not_expecting_results_get_no_results(self):
        response = self.client.get(self.url, {"tag": "pig"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

class StoryListAPIViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.url = reverse("story:story-list")
        self.story1 = Story.objects.create(
            title="testtitle", 
            user=self.user, 
            slug="testtitle",
            is_published=True)
        self.story2 = Story.objects.create(
            title="testtitle2", 
            user=self.user, 
            slug="testtitle2")
        self.story3 = Story.objects.create(
            title="testtitle3", 
            user=self.user, 
            slug="testtitle3",
            is_published=True)

    def test_list_stories(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

class StoryListAdminAPIViewTestCase(ExistingStoryTestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("story:story-list-admin")
        cls.user_admin = User.objects.create_user(
            alias="admin", username="admin", password="testpassword", type="administrator"
        )

    def test_when_admin_returns_okay(self):
        self.client.force_authenticate(user=self.user_admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 3)

    def test_when_not_admin_returns_forbidden(self):
        self.client.force_authenticate(user=self.catuser)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_when_not_authorized_returns_unauthorized(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class StoryMineAPIViewTestCase(ExistingStoryTestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("story:story-mine")

    def test_with_published_returns_okay(self):
        self.client.force_authenticate(user=self.catuser)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        serializer = StorySerializer(self.catstory1)
        self.assertEqual(serializer.data, response.data["results"][0])

    def test_with_draft_returns_okay(self):
        self.client.force_authenticate(user=self.catuser)
        response = self.client.get(self.url, {"draft": 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        serializer = StorySerializer(self.catstory2)
        self.assertEqual(serializer.data, response.data["results"][0])    

    def test_when_not_authenticated_returns_unauthorized(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class StoryFeaturedAPIView(ExistingStoryTestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("story:story-featured")

    def test_when_authenticated_returns_okay(self):
        self.client.force_authenticate(user=self.catuser)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = StorySerializer(self.catstory1)
        self.assertEqual(serializer.data, response.data[0])

    def test_when_not_authenticated_returns_ok(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = StorySerializer(self.catstory1)
        self.assertEqual(serializer.data, response.data[0])

#Filter by... test cases 
class StoryByCategoryView(ExistingStoryTestCase):

    def setUp(self):
        super().setUp()
        self.url = reverse("story:by-category", args = [self.category1.id])

    def test_when_authenticated_returns_okay(self):
        self.client.force_authenticate(user=self.catuser)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        serializer = StorySerializer(self.catstory1)
        self.assertEqual(serializer.data, response.data["results"][0])

    def test_when_not_authenticated_returns_ok(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        serializer = StorySerializer(self.catstory1)
        self.assertEqual(serializer.data, response.data["results"][0])

class StoryByTagView(ExistingStoryTestCase):

    def setUp(self):
        super().setUp()
        self.url = reverse("story:by-tag", args = [self.cattag.id])

    def test_when_authenticated_returns_okay(self):
        self.client.force_authenticate(user=self.catuser)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        serializer = StorySerializer(self.catstory1)
        self.assertEqual(serializer.data, response.data["results"][0])

    def test_when_not_authenticated_returns_ok(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        serializer = StorySerializer(self.catstory1)
        self.assertEqual(serializer.data, response.data["results"][0])        

class StoryByTagAuthor(ExistingStoryTestCase):

    def setUp(self):
        super().setUp()
        self.url = reverse("story:by-author", args = [self.catuser.id])

    def test_when_authenticated_returns_okay(self):
        self.client.force_authenticate(user=self.catuser)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        serializer = StorySerializer(self.catstory1)
        self.assertEqual(serializer.data, response.data["results"][0])

    def test_when_not_authenticated_returns_ok(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        serializer = StorySerializer(self.catstory1)
        self.assertEqual(serializer.data, response.data["results"][0])              
