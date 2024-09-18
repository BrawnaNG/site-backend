from rest_framework.permissions import BasePermission, IsAuthenticated


class IsAuth(IsAuthenticated, BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == "GET":
            return True
        return request.user.is_authenticated


class IsUserType(BasePermission):
    user_type = ""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return (
            request.user.groups.filter(name=self.user_type).exists()
            or request.user.type == self.user_type
            or request.user.groups.filter(name="Administrator").exists()
            or request.user.type == "administrator"
        )

    def has_object_permission(self, request, view, obj):
        if request.method == "GET":
            return True
        return self.has_permission(request, view)


class IsAuthor(IsUserType):
    user_type = "author"


class IsAdmin(IsUserType):
    user_type = "administrator"


class IsReader(IsUserType):
    user_type = "reader"
