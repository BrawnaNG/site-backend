from django.urls import path

from category.views import (
    CategoryCreateAPIView,
    CategoryListAPIView,
    CategoryRetrieveUpdateDestroyAPIView,
)

app_name = "category"
urlpatterns = [
    path("/list/", CategoryListAPIView.as_view(), name="category-list"),
    path("/add/", CategoryCreateAPIView.as_view(), name="category-create"),
    path(
        "/change/<str:name>/",
        CategoryRetrieveUpdateDestroyAPIView.as_view(),
        name="category-detail",
    ),
]
