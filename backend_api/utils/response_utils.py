# backend_api/utils/response_utils.py
from rest_framework.response import Response
from rest_framework import status


def success_response(message, data=None, status_code=status.HTTP_200_OK):
    return Response(
        {"success": True, "message": message, "data": data or []}, status=status_code
    )


def error_response(message, status_code=status.HTTP_400_BAD_REQUEST, errors=None):
    if isinstance(message, dict):
        errors = message
        message = "Validation Error"
    
    response_data = {"success": False, "message": message}
    if errors:
        response_data["errors"] = errors
        
    return Response(response_data, status=status_code)
