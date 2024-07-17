from django.core.cache import cache

from chat.models import Artist, Collector, Chat, User
from palette.models import Artwork

from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.exceptions import NotFound, PermissionDenied, NotAuthenticated


class IsChatArtistOrCollector(BasePermission):
    def has_permission(self, request, view):
        chat_id = view.kwargs.get("chat_id")
        chat = Chat.objects.filter(id=chat_id).first()
        if not chat:
            raise NotFound("Chat does not exist.")
        elif request.user not in (chat.artist.user, chat.collector.user):
            raise PermissionDenied("You must be a member of this chat to access it.")
        else:
            return True
        
    
class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated and request.method not in SAFE_METHODS:
            raise NotAuthenticated
        elif all([(request.user.is_authenticated and not request.user.is_superuser), request.method not in SAFE_METHODS]):
            raise PermissionDenied("You must be an admin to perform this action.")
        else:
            return True
        
        
class IsArtistOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        artists_user_list = [str(id) for id in Artist.objects.values_list("user_id", flat=True)]
        if any([(request.user.is_authenticated and str(request.user.id) in artists_user_list), request.method in SAFE_METHODS]):
            return True
        else:
            raise PermissionDenied("You must be an artist to perform this action.")
        
        
class IsCreatorOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        artwork_slug = view.kwargs.get("slug")
        artwork = Artwork.available.filter(slug=artwork_slug).first()
        if not artwork:
            raise NotFound("Artwork does not exist.")
        
        if not any([all([request.user.is_authenticated, (str(artwork.artist.user.id) == str(request.user.id))]), request.method in SAFE_METHODS]):
            raise PermissionDenied("You must be the artwork's creator to perform this action.")
        else:
            return True
        
class IsCollectorOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        collectors_user_list = [str(id) for id in Collector.objects.values_list("user_id", flat=True)]
        if not (request.user.is_authenticated and str(request.user.id) in collectors_user_list):
            raise PermissionDenied("You must be a collector to perform this action.")
        else:
            return True
        
class IsCurrentOwnerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        profile_id = view.kwargs.get("profile_id")
        profile = Artist.objects.filter(id=profile_id).first()
        if not profile:
            profile = Collector.objects.filter(id=profile_id).first()
            
        if not profile:
            raise NotFound("Profile does not exist.")
        elif not any([(str(profile.user.id) == str(request.user.id)), request.method in SAFE_METHODS]):
            raise PermissionDenied("You are not allowed to operate on another user's profile.")
        else:
            return True
        

