from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from django.http import HttpResponseNotFound
from accounts.permissions import IsAuth, IsAuthor, IsOwnerOrAdmin
from category.models import Category
from tag.models import Tag

from .models import Story
from .serializers import (
    StorySerializer,
    StoryDetailSerializer,
    StoryCreatorSerializer
)

from tag.serializers import TagSearchSerializer
    
class StoryRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = "id"
    queryset = Story.objects.all()
    serializer_class = StorySerializer
    permission_classes = [IsAuthor]

class StoryDetailAPIView(generics.RetrieveAPIView):
    lookup_field = "id"
    queryset = Story.objects.all()
    serializer_class = StoryDetailSerializer
    permission_classes = []

class StoryCreateAPIView(generics.CreateAPIView):
    serializer_class = StoryCreatorSerializer
    permission_classes = [IsAuthor]

    def create(self, request, *args, **kwargs):
        try:
            data = request.data.copy()
            data["user"] = self.request.user.id
            serializer = self.serializer_class(data=data)
            if (serializer.is_valid()):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": "Unable to create story"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response({"error": "Unable to create story"}, status=status.HTTP_400_BAD_REQUEST)

class StorySaveAPIView(generics.UpdateAPIView):
    serializer_class = StorySerializer
    permission_classes = [IsOwnerOrAdmin]
    queryset = Story.objects.all()
    lookup_field = "id"

    def get_object(self):
        return self.queryset.get(id=self.kwargs.get("id"))

    def put(self, request, *args, **kwargs):
        story = self.get_object()
        data = request.data.copy()

        tags = data.pop("tags", [])
        if tags:
            new_tags = [x for x in tags if not x.get('id')]
            tag_ids = [x['id'] for x in tags if x.get('id')]            
            for (tag) in new_tags:
                existing_tag = Tag.objects.filter(name__iexact=tag["name"])
                if (existing_tag):
                    tag_ids.append(existing_tag.id)
                else:
                    serializer = TagSearchSerializer(data=tag)
                    if (serializer.is_valid()):
                        new_tag = serializer.save(user=self.request.user)
                        tag_ids.append(new_tag.id)
            data["tags"] = list(tag_ids)
        else:
            data["tags"] = []

        categories = data.pop("categories", [])
        if categories:
            category_ids = [x['id'] for x in categories]
            check_ids = Category.objects.filter(id__in=category_ids).values_list(
                "id", flat=True
            )
            if len(check_ids) != len(category_ids):
                raise NotFound("Category not found!")
            data["categories"] = list(category_ids)
        else:
            data["categories"] = []

        serializer = self.get_serializer(data=data)

        if serializer.is_valid():
            title = serializer.validated_data["title"]
            is_published = serializer.validated_data["is_published"]
            has_chapters = serializer.validated_data["has_chapters"]
            tags = serializer.validated_data["tags"]
            categories = serializer.validated_data["categories"]
            story.title = title
            story.is_published = is_published
            story.has_chapters = has_chapters
            story.tags.set(tags)
            story.categories.set(categories)
            story.save()
            return Response({"status": "story saved"})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class AddSavedStoryAPIView(generics.UpdateAPIView):
    serializer_class = StorySerializer
    permission_classes = [IsAuth]

    def put(self, request, *args, **kwargs):
        user = request.user
        story_id = self.kwargs.get("id")
        try:
            story = Story.objects.get(id=story_id)
        except Story.DoesNotExist:
            raise NotFound("Story not found!")

        user.saved_stories.add(story)
        return Response({"detail": "Story added to saved stories successfully."})

class DeleteSavedStoryAPIView(generics.DestroyAPIView):
    serializer_class = StorySerializer
    permission_classes = [IsAuth]

    def delete(self, request, *args, **kwargs):
        user = request.user
        story_id = self.kwargs.get("id")
        try:
            story = user.saved_stories.get(id=story_id)
        except Story.DoesNotExist:
            raise NotFound("Story not found in saved stories!")

        user.saved_stories.remove(story)
        return Response({"detail": "Story removed from saved stories successfully."})
    
class StoryCheckAuthorAPIView(generics.GenericAPIView):
    permission_classes = [IsAuth]

    def get(self, request, *args, **kwargs):
        user = request.user
        story_id = self.kwargs.get("id")
        is_author = False
        try:
            story = Story.objects.get(id=story_id)
            if story.user == user :
                is_author = True
        except Story.DoesNotExist:
            return HttpResponseNotFound() 
            
        return Response(is_author, status=status.HTTP_200_OK)