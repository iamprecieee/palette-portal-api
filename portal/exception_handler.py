from rest_framework.views import exception_handler
from rest_framework.exceptions import Throttled, ValidationError


# Overriding REST framework's exception handler to customize error response data
def palette_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, Throttled):
        response.data = exc.detail

    if isinstance(exc, ValidationError):
        error_list = []
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
                else:
                    error_list.append(error)

        if len(error_list) == 1:
            error_list = error_list[0]

        response.data = error_list

    return response
