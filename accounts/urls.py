from django.urls import path

from .views import (
    ActivationAPIView,
    ChangePasswordView,
    DisableUserAPIView,
    LastUsersAPIView,
    RegistrationAPIView,
    UsersListAPIView,
)

app_name = "accounts"
urlpatterns = [
    path("/registration/", RegistrationAPIView.as_view(), name="registration"),
    path("/activation/<str:token>/", ActivationAPIView.as_view(), name="activation"),
    path("/last-user/", LastUsersAPIView.as_view(), name="last_users"),
    path("/list/", UsersListAPIView.as_view(), name="users_list"),
    path("/change-password-admin/<str:email>/", ChangePasswordView.as_view()),
    path("/disable-user-admin/<str:email>/", DisableUserAPIView.as_view()),
]
