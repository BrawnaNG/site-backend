from django.urls import path

from category.views import (
    CategoryCreateAPIView,
    CategoryListAPIView,
    CategoryUpdateAPIView,
    CategoryRetrieveAPIView,
    CategoryDeleteAPIView
)

app_name = "category"
urlpatterns = [
    path("/list/", CategoryListAPIView.as_view(), name="category-list"),
    path("/add/", CategoryCreateAPIView.as_view(), name="category-create"),
    path(
        "/change/<int:id>/",
        CategoryUpdateAPIView.as_view(),
        name="category-edit",
    ),
        path(
        "/remove/<int:id>/",
        CategoryDeleteAPIView.as_view(),
        name="category-delete",
    ),
    path("/info/<int:id>/",CategoryRetrieveAPIView.as_view(),name="category-info"),
]
