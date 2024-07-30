from django.urls import resolve

from user.models import JWTAccessToken

from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import AllowAny


# Method to retrieve permission classes of the request's view
def get_permission_classes_app_names(request):
    resolver_match = resolve(request.path_info)
    view_func = resolver_match.func
    view_class = getattr(view_func, "view_class", None)
    permission_classes = getattr(view_class, "permission_classes", [])
    app_names = resolver_match.app_names
    
    return permission_classes, app_names
    

class JWTBlacklistMiddleware:
    """
    For checking access tokens to ensure they are not blacklisted.
    Used JSONRenderer to render the content of rest_framework's `Response` object.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        permission_classes, app_names = get_permission_classes_app_names(request)
        if AllowAny in permission_classes or "admin" in app_names:
            return self.get_response(request)
        
        token = request.headers.get("Authorization")
        if token and "Bearer" in token:
            access_token = token.split(" ")[1]
            access_token_list = [str(token) for token in JWTAccessToken.objects.values_list("token", flat=True)]
            if str(access_token) not in access_token_list:
                response = Response("Invalid authentication token. Log in again.", status=status.HTTP_401_UNAUTHORIZED) 
                response.accepted_renderer = JSONRenderer()
                response.accepted_media_type = "application/json"
                response.renderer_context = {}
                response.render()
                return response

        return self.get_response(request)
    
    
class ClearAuthHeaders:
    """ 
    For removing Authentication headers from 'anonymous' endpoints such as Register, Login...
    """
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        permission_classes, app_names = get_permission_classes_app_names(request)
        token = request.META.get("HTTP_AUTHORIZATION")
        if token and AllowAny in permission_classes:
            request.META.pop("HTTP_AUTHORIZATION")
        return self.get_response(request)
            
