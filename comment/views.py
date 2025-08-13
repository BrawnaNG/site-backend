from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdmin, IsAuth
from story.models import Story

from .models import Comment
from .serializers import CommentSerializer


class CommentListAPIView(generics.ListAPIView):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()

    def get_queryset(self):
        try:
            story = Story.objects.get(id=self.kwargs["storyid"])
        except Exception:
            raise ValidationError("Invalid story id provided.")
        queryset = Comment.objects.filter(story=story)
        return queryset


class CommentListAdminAPIView(generics.ListAPIView):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all().order_by("-created_at")
    permission_classes = [IsAdmin]
    pagination_class = PageNumberPagination


class CommentCreateAPIView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuth]

    def perform_create(self, serializer):
        try:
            story_id = self.kwargs["storyid"]
            story = Story.objects.get(id=story_id)
            serializer.save(user=self.request.user, story=story)
        except Story.DoesNotExist:
            raise ValidationError("Invalid story id provided.")
        except KeyError:
            raise ValidationError("Story id is missing from URL.")


class CommentRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuth]


class UserCommentListAPIView(generics.ListAPIView):
    permission_classes = [IsAuth]
    pagination_class = PageNumberPagination

    def get(self, request):
        user_comments = Comment.objects.filter(user=request.user).order_by(
            "-created_at"
        )
        page = self.paginate_queryset(user_comments)
        if page is not None:
            serializer = CommentSerializer(user_comments, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = CommentSerializer(user_comments, many=True)
        return Response(serializer.data)