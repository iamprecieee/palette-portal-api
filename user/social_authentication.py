from django.contrib.auth import REDIRECT_FIELD_NAME

from .refresh import SessionRefreshToken
from .tasks import store_access_token, send_otp

from social_core.actions import do_auth
from social_core.utils import user_is_authenticated, user_is_active, partial_pipeline_data
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


def begin_social_authentication(request, backend):
    return do_auth(request.backend, redirect_name=REDIRECT_FIELD_NAME)


def complete_social_authentication(request, backend):
    backend = request.backend
    user = request.user
    
    # Check if user is authenticated
    is_authenticated = user_is_authenticated(user)
    user = user if is_authenticated else None
    partial = partial_pipeline_data(backend, user)
    if partial:
        user = backend.continue_pipeline(partial)
        backend.clean_partial_pipeline(partial.token)
    else:
        user = backend.complete(user=user)
        
    # Check if the output value is something other than a user object
    user_model = backend.strategy.storage.user.user_model()
    if user and not isinstance(user, user_model):
        return Response("Provided 'user' is not a valid User object.")
    
    if user:
        if user_is_active(user):
            is_new = getattr(user, "is_new", False)
            if is_new:
                send_otp.delay(user.email, otp_type="password")
                return Response("User created successfully. A link has been sent to your email address. Click it to update your password and/or proceed to login.", status=status.HTTP_201_CREATED)
            else:
                refresh_token = RefreshToken.for_user(user)
                access_token = refresh_token.access_token
                
                refresh = SessionRefreshToken(request)
                refresh.remove()
                refresh.add(str(refresh_token))
                store_access_token.delay(str(access_token))
                
                return Response({
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "access": str(access_token),
                    "refresh": str(refresh_token),
                }, status=status.HTTP_200_OK)
        else:
            return Response("User is inactive.", status=status.HTTP_400_BAD_REQUEST)

