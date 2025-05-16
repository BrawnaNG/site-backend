from django.urls import path

from tag.views import (
    TagAddAPIView, 
    TagListAPIView, 
    TagUpdateView,
    TagRetrieveView,
    TagDestroyView
)

app_name = "tag"


urlpatterns = [
    path("/add/", TagAddAPIView.as_view(), name="tag-add"),
    path(
        "/change/<str:name>/",
        TagUpdateView.as_view(),
        name="tag-update",
    ),
    path(
        "/remove/<str:name>/",
        TagDestroyView.as_view(),
        name="tag-remove",
    ),
    path(
        "/info/<int:id>/",
        TagRetrieveView.as_view(),
        name="tag-info",
    ),
    path("/", TagListAPIView.as_view(), name="tag-list"),
]
