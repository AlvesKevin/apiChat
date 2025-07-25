from django.http import JsonResponse
from django.shortcuts import redirect
from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema

@extend_schema(exclude=True)
@api_view(['GET'])
def home(request):
    """Redirection vers la documentation API"""
    return JsonResponse({
        'message': 'Bienvenue sur l\'API ChatBot',
        'version': '1.0.0',
        'documentation': {
            'swagger_ui': request.build_absolute_uri('/api/docs/'),
            'redoc': request.build_absolute_uri('/api/redoc/'),
            'openapi_schema': request.build_absolute_uri('/api/schema/')
        },
        'endpoints': {
            'register': request.build_absolute_uri('/register'),
            'login': request.build_absolute_uri('/login'),
            'users': request.build_absolute_uri('/users'),
            'messages': request.build_absolute_uri('/messages')
        }
    })