from django.db.models import ( 
    Q, 
    F 
)
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError

from rest_framework.response import Response
from accounts.permissions import IsAuthor, IsOwnerOrAdmin
import html

from .models import Story, Chapter, StoryChapters
from .serializers import (
    ChapterSerializer,
    ChapterDetailSerializer
)
    
class ChapterDetailAPIView(generics.RetrieveAPIView):
    lookup_field = "id"
    queryset = Chapter.objects.all()
    serializer_class = ChapterDetailSerializer
    permission_classes = []
    
class ChapterCreateAPIView(generics.CreateAPIView):
    serializer_class = ChapterSerializer
    permission_classes = [IsOwnerOrAdmin]

    def create(self, request, *args, **kwargs):
        try:
            data = request.data.copy()
            pos = data.pop("pos")
            story_id = self.kwargs["storyid"]
            story = Story.objects.get(id=story_id)
            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                serializer.save(user=self.request.user)
                StoryChapters.objects.filter(
                    Q(story=story)
                    & Q(order__gte=pos)).update(order=F('order')+1)
                StoryChapters.objects.create(story=story,chapter=serializer.instance,order=pos)
                return Response(
                    data=serializer.data, status=status.HTTP_201_CREATED
        )
        except Story.DoesNotExist:
            raise ValidationError("Invalid story id provided.")
        except KeyError:
            raise ValidationError("Story id is missing from URL.")

class ChapterSaveAPIView(generics.UpdateAPIView):
    serializer_class = ChapterSerializer
    permission_classes = [IsOwnerOrAdmin]
    queryset = Chapter.objects.all()
    
    def put(self, request, *args, **kwargs):
        try:
            chapter = self.queryset.get(id=self.kwargs.get("id"))
            data = request.data.copy()
            data["body"] = html.escape(data.pop("body"))
            data["title"] = data.pop("title")
            serializer = self.get_serializer(data=data)

            if serializer.is_valid():
                title = serializer.validated_data["title"]
                body = serializer.validated_data["body"]
                chapter.title = title
                chapter.body = body
                chapter.save()
                return Response({"status": "chapter saved"})
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Chapter.DoesNotExist:
            return Response("Chapter does not exist", status=status.HTTP_404_NOT_FOUND)
        except StoryChapters.DoesNotExist:
            raise ValidationError("Orphan chapter")

class ChapterDeleteAPIView(generics.DestroyAPIView):
    permission_classes = [IsOwnerOrAdmin]
    queryset = Chapter.objects.all()
    lookup_field = "id"

    def get_object(self):
        return self.queryset.get(id=self.kwargs.get("id"))

    def delete(self, request, *args, **kwargs):
        try:
            chapter = self.queryset.get(id=self.kwargs.get("id"))
            storychapter = StoryChapters.objects.get(chapter=chapter)
            pos = storychapter.order
            storychapter.delete()
            chapter.delete()
            StoryChapters.objects.filter(
                Q(story=storychapter.story)
                & Q(order__gt=pos)).update(order=F('order')-1)
        except Chapter.DoesNotExist:
            return Response("Chapter does not exist", status=status.HTTP_404_NOT_FOUND)
        except StoryChapters.DoesNotExist:
            raise ValidationError("Orphan chapter")
        return Response("Chapter deleted", status=status.HTTP_200_OK)
