from rest_framework.views import exception_handler
from rest_framework.exceptions import Throttled


def palette_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    if isinstance(exc, Throttled):
        response.data = exc.detail
        
    return response
    