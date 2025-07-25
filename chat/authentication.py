import jwt
import logging
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from functools import wraps

User = get_user_model()
logger = logging.getLogger('chat.authentication')

def create_jwt_token(user):
    payload = {
        'user_id': user.id,
        'username': user.username
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm='HS256')
    return token

def decode_jwt_token(token):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def jwt_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        token = request.headers.get('x-api-key')
        logger.debug(f"JWT Auth check for {request.path}")
        
        if not token:
            logger.warning(f"Missing token for {request.path}")
            return JsonResponse({'error': 'Token required'}, status=401)
        
        logger.debug(f"Token received: {token[:20]}...")
        payload = decode_jwt_token(token)
        if not payload:
            logger.warning(f"Invalid token for {request.path}")
            return JsonResponse({'error': 'Invalid token'}, status=401)
        
        try:
            user = User.objects.get(id=payload['user_id'])
            request.user = user
            logger.debug(f"JWT auth successful for user: {user.username} (ID: {user.id})")
        except User.DoesNotExist:
            logger.error(f"User not found for token payload: {payload}")
            return JsonResponse({'error': 'User not found'}, status=401)
        
        return view_func(request, *args, **kwargs)
    return wrapper