from django.urls import path

from .views import (
    CreateSaveStoryAPIView,
    DeleteSavedStoryAPIView,
    SavedStoriesAPIView,
    SearchView,
    StoryCreateAPIView,
    StoryDetailAPIView,
    StoryListAPIView,
    StoryMineAPIView,
    StoryRetrieveUpdateDestroyAPIView,
    StoryFeaturedAPIView,
)

app_name = "story"

urlpatterns = [
    path(
        "/change/<slug:slug>/",
        StoryRetrieveUpdateDestroyAPIView.as_view(),
        name="story-change",
    ),
    path("/add/", StoryCreateAPIView.as_view(), name="story-create"),
    path("/search/", SearchView.as_view(), name="search"),
    path("/list/", StoryListAPIView.as_view(), name="story-list"),
    path("/mine/", StoryMineAPIView.as_view(), name="story-mine"),
    path("/featured/", StoryFeaturedAPIView.as_view(), name="story-featured"),
    path("/search/", SearchView.as_view()),
    path("/detail/<slug:slug>/", StoryDetailAPIView.as_view(), name="story-detail"),
    path("/save-story-list/", SavedStoriesAPIView.as_view()),
    path("/save-story/<str:story_slug>/", CreateSaveStoryAPIView.as_view()),
    path("/delete-saved-story/<str:story_slug>/", DeleteSavedStoryAPIView.as_view()),
]
