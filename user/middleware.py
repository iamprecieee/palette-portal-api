from .models import JWTTokenBlacklist

from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer


class JWTBlacklistMiddleware:
    """
    For checking access tokens to ensure they are not blacklisted.
    Used JSONRenderer to render the content of rest_framework's `Response` object.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = request.headers.get("Authorization")
        if token:
            token = token.split(" ")[1]
        if JWTTokenBlacklist.objects.filter(token=token).exists():
            response = Response("Invalid token.", status=status.HTTP_401_UNAUTHORIZED)
            response.accepted_renderer = JSONRenderer()
            response.accepted_media_type = "application/json"
            response.renderer_context = {}
            response.render()

            return response

        return self.get_response(request)
