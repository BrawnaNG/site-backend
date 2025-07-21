"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

from .views import MyTokenObtainPairView, verify_recaptcha

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/accounts", include("accounts.urls", namespace="accounts")),
    path("api/v1/category", include("category.urls", namespace="category")),
    path("api/v1/comment", include("comment.urls", namespace="comment")),
    path("api/v1/story", include("story.urls", namespace="story")),
    path("api/v1/tag", include("tag.urls", namespace="tag")),
    path("api/v1/token/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/v1/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/v1/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("api/v1/verify-recaptcha/", verify_recaptcha, name="verify_recaptcha"),
]
