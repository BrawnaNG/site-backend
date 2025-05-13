from django.urls import path

from category.views import (
    CategoryCreateAPIView,
    CategoryListAPIView,
    CategoryUpdateAPIView,
    CategoryRetrieveAPIView
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
    path("/info/<int:id>/",CategoryRetrieveAPIView.as_view(),name="category-info"),
]
