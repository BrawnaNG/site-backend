from rest_framework.permissions import BasePermission, IsAuthenticated
from .models import Story
from django.db.models import Q

class IsAuth(IsAuthenticated, BasePermission):
    def has_object_permission(self, request, view, obj):
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
        return self.has_permission(request, view)

class IsOwnerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.groups.filter(name="Administrator").exists() or request.user.type == "administrator":
            return True
        if not (request.user.groups.filter(name="author").exists()
            or request.user.type == "author"):
            return False
        
        story_id = view.kwargs.get('storyid')
        if story_id is None:
            story_id = view.kwargs.get('id')
        
        if story_id is not None:
            return Story.objects.all().filter(
                Q(id=story_id ) & Q(user=request.user)).exists()
    
        return False
                        

class IsAuthor(IsUserType):
    user_type = "author"


class IsAdmin(IsUserType):
    user_type = "administrator"


class IsReader(IsUserType):
    user_type = "reader"
