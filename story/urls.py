from django.urls import path

from .views import (
    SaveStoryAPIView,
    DeleteSavedStoryAPIView,
    SavedStoriesAPIView,
    SearchStoryView,
    SearchAuthorView,
    SearchTagView,
    StoryCreateAPIView,
    StoryDetailAPIView,
    StoryListAPIView,
    StoryMineAPIView,
    StoryRetrieveUpdateDestroyAPIView,
    StoryFeaturedAPIView,
    ChapterCreateAPIView,
    ChapterDetailAPIView,
    SaveChapterAPIView,
    StoryListAdminAPIView
)

app_name = "story"

urlpatterns = [
    path(
        "/change/<int:id>/",
        StoryRetrieveUpdateDestroyAPIView.as_view(),
        name="story-change",
    ),
    path("/add/", StoryCreateAPIView.as_view(), name="story-create"),
    path("/<int:storyid>/chapter/add/", ChapterCreateAPIView.as_view(), name="chapter-create"),
    path("/search/story", SearchStoryView.as_view(), name="search"),
    path("/search/author", SearchAuthorView.as_view(), name="search"),
    path("/search/tag", SearchTagView.as_view(), name="search"),
    path("/list/", StoryListAPIView.as_view(), name="story-list"),
    path("/list-admin/", StoryListAdminAPIView.as_view(), name="story-list-admin"),
    path("/mine/", StoryMineAPIView.as_view(), name="story-mine"),
    path("/featured/", StoryFeaturedAPIView.as_view(), name="story-featured"),
    path("/detail/<int:id>/", StoryDetailAPIView.as_view(), name="story-detail"),
    path("/chapter/<int:id>/", ChapterDetailAPIView.as_view(), name="chapter-detail"),
    path("/save-story-list/", SavedStoriesAPIView.as_view()),
    path("/save-story/<int:id>/", SaveStoryAPIView.as_view()),
    path("/save-chapter/<int:id>/", SaveChapterAPIView.as_view()),
    path("/delete-saved-story/<int:id>/", DeleteSavedStoryAPIView.as_view()),
]
