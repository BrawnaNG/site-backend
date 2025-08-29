from django.urls import path

from .story_views import (
    StorySaveAPIView,
    StoryCreateAPIView,
    StoryDetailAPIView,
    StoryRetrieveUpdateDestroyAPIView,
    AddSavedStoryAPIView,
    DeleteSavedStoryAPIView,
    StoryCheckAuthorAPIView,
)

from .chapter_views import (
    ChapterCreateAPIView,
    ChapterDetailAPIView,
    ChapterSaveAPIView,
    ChapterDeleteAPIView,
)

from .search_views import (
    SearchStoryView,
    SearchAuthorView,
    SearchTagView,
    SavedStoriesAPIView,
    StoryFeaturedAPIView,
    StoryListAPIView,
    StoryMineAPIView,
    StoryListAdminAPIView,
)

from .by_views import (
    ByCategoryView,
    ByTagView,
    ByAuthorView
)



app_name = "story"

urlpatterns = [
    #story paths
    path(
        "/change/<int:id>/",
        StoryRetrieveUpdateDestroyAPIView.as_view(),
        name="story-change",
    ),
    path("/add/", StoryCreateAPIView.as_view(), name="story-create"),
    path("/save-story/<int:id>/", StorySaveAPIView.as_view(), name="story-save"),
    path("/detail/<int:id>/", StoryDetailAPIView.as_view(), name="story-detail"),
    path("/check-author/<int:id>/", StoryCheckAuthorAPIView.as_view(), name="story-check-author"),

    # saved stories
    path("/add-saved-story/<int:id>/", AddSavedStoryAPIView.as_view(), name="story-saved-add"),
    path("/delete-saved-story/<int:id>/", DeleteSavedStoryAPIView.as_view(), name="story-saved-delete"),
    path("/save-story-list/", SavedStoriesAPIView.as_view(), name="story-saved-list"),

    #chapter paths
    path("/chapter/<int:id>/", ChapterDetailAPIView.as_view(), name="chapter-detail"),
    path("/<int:storyid>/chapter-add/", ChapterCreateAPIView.as_view(), name="chapter-create"),
    path("/<int:storyid>/chapter-save/<int:id>/", ChapterSaveAPIView.as_view(), name="chapter-save"),
    path("/<int:storyid>/chapter-delete/<int:id>/", ChapterDeleteAPIView.as_view(), name="chapter-delete"),

    #search and list views
    path("/search/story", SearchStoryView.as_view(), name="search-story"),
    path("/search/author", SearchAuthorView.as_view(), name="search-author"),
    path("/search/tag", SearchTagView.as_view(), name="search-tag"),
    path("/list/", StoryListAPIView.as_view(), name="story-list"),
    path("/list-admin/", StoryListAdminAPIView.as_view(), name="story-list-admin"),
    path("/mine/", StoryMineAPIView.as_view(), name="story-mine"),
    path("/featured/", StoryFeaturedAPIView.as_view(), name="story-featured"),

    #filter by category, tag, or author
    path("/bycategory/<int:id>", ByCategoryView.as_view(), name="by-category"),
    path("/bytag/<int:id>", ByTagView.as_view(), name="by-tag"),
    path("/byauthor/<int:id>", ByAuthorView.as_view(), name="by-author"),


    
    
    

    
    
]
