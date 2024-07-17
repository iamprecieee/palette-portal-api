from django.db import IntegrityError
from django.core.exceptions import ValidationError as CoreValidationError

from rest_framework.views import exception_handler
from rest_framework.exceptions import (
    Throttled,
    ValidationError,
    AuthenticationFailed,
    NotAuthenticated,
    PermissionDenied,
    NotFound,
)
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework.response import Response
from rest_framework import status


# Overriding REST framework's exception handler to customize error response data
def palette_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, (Throttled, NotFound)):
        response.data = exc.detail

    if isinstance(exc, ValueError):
        response = Response(
            exc.args[0].capitalize(), status=status.HTTP_400_BAD_REQUEST
        )

    if isinstance(exc, (AuthenticationFailed, NotAuthenticated, PermissionDenied)):
        try:
            if exc.detail and exc.detail["code"] == "user_not_found":
                response.data = exc.detail["detail"]
            elif exc.detail and exc.detail["code"] == "permission_denied":
                response.data = exc.detail["detail"]
            else:
                response.data = exc.detail["messages"][0]["message"]
        except:
            response.data = exc.detail

    if isinstance(exc, TokenError):
        response = Response(exc.args)
        # response.data = InvalidToken(TokenError.args)

    if isinstance(exc, IntegrityError):
        response = Response(exc.args[0].capitalize(), status=status.HTTP_409_CONFLICT)

    if isinstance(exc, CoreValidationError):
        response = Response(str(exc).strip("[]'"), status=status.HTTP_400_BAD_REQUEST)

    if isinstance(exc, PermissionError):
        response = Response(exc.args[0], status=status.HTTP_403_FORBIDDEN)

    if isinstance(exc, ValidationError):
        error_list = []
        try:
            for key, value in exc.detail.items():
                for error in value:
                    if error.code == "blank":
                        error_list.append(f"{key.title()} field cannot be blank.")
                    elif error.code == "required":
                        error_list.append(f"{key.title()} field is required.")
                    elif error.code == "unique":
                        error_list.append(error.capitalize())
                    elif error.code == "invalid_choice":
                        error_list.append(error.replace('"', ""))
                    elif error.code == "invalid":
                        error_list.append(f"{key.title()} error. {error}")
                    else:
                        error_list.append(error)
        except:
            for key, value in exc.detail.items():
                if value.code == "invalid":
                    error_list.append(f"{key.title()} error. {value}")

        if len(error_list) == 1:
            error_list = error_list[0]

        response.data = error_list

    return response
