from django.urls import path

from .views import (
    SaveStoryAPIView,
    DeleteSavedStoryAPIView,
    SavedStoriesAPIView,
    SearchView,
    StoryCreateAPIView,
    StoryDetailAPIView,
    StoryListAPIView,
    StoryMineAPIView,
    StoryRetrieveUpdateDestroyAPIView,
    StoryFeaturedAPIView,
    ChapterCreateAPIView,
)

app_name = "story"

urlpatterns = [
    path(
        "/change/<int:id>/",
        StoryRetrieveUpdateDestroyAPIView.as_view(),
        name="story-change",
    ),
    path("/add/", StoryCreateAPIView.as_view(), name="story-create"),
    path("/chapter/add", ChapterCreateAPIView.as_view(), name="chapter-create"),
    path("/search/", SearchView.as_view(), name="search"),
    path("/list/", StoryListAPIView.as_view(), name="story-list"),
    path("/mine/", StoryMineAPIView.as_view(), name="story-mine"),
    path("/featured/", StoryFeaturedAPIView.as_view(), name="story-featured"),
    path("/search/", SearchView.as_view()),
    path("/detail/<int:id>/", StoryDetailAPIView.as_view(), name="story-detail"),
    path("/save-story-list/", SavedStoriesAPIView.as_view()),
    path("/save-story/<int:id>/", SaveStoryAPIView.as_view()),
    path("/delete-saved-story/<int:id>/", DeleteSavedStoryAPIView.as_view()),
]
