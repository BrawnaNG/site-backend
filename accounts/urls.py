from django.urls import path

from .views import (
    ActivationAPIView,
    ChangePasswordView,
    DisableUserAPIView,
    LastUsersAPIView,
    RegistrationAPIView,
    UsersListAPIView,
    UserRoleListAPIView,
    AuthorRetrieveView,
    ResetPasswordAPIView,
    ApplyResetPasswordAPIView,
)

app_name = "accounts"
urlpatterns = [
    path("/registration/", RegistrationAPIView.as_view(), name="registration"),
    path("/activation/<str:token>/", ActivationAPIView.as_view(), name="activation"),
    path("/last-user/", LastUsersAPIView.as_view(), name="last-users"),
    path("/list/", UsersListAPIView.as_view(), name="users-list"),
    path("/role/", UserRoleListAPIView.as_view(), name="user-role"),
    path("/change-password-admin/<str:email>/", ChangePasswordView.as_view(), name="change-password"),
    path("/disable-user-admin/<str:email>/", DisableUserAPIView.as_view()),
    path("/reset-password/", ResetPasswordAPIView.as_view(), name="reset-password"),
    path("/apply-reset-password/", ApplyResetPasswordAPIView.as_view(), name="apply-reset-password"),
    path(
        "/info/<int:id>/",
        AuthorRetrieveView.as_view(),
        name="author-info",
    ),
]
