import json
import base64
import logging
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from django.db import models
from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema, OpenApiExample
from drf_spectacular.openapi import OpenApiParameter
from .models import Message
from .authentication import create_jwt_token, jwt_required
from .serializers import (
    RegisterSerializer, LoginSerializer, LoginResponseSerializer,
    SendMessageSerializer, UsersResponseSerializer, MessagesResponseSerializer,
    SuccessResponseSerializer, ErrorResponseSerializer
)

logger = logging.getLogger('chat.views')

User = get_user_model()

@extend_schema(
    operation_id='register_user',
    summary='Inscription d\'un nouvel utilisateur',
    description='Créer un nouveau compte utilisateur avec nom d\'utilisateur et mot de passe.',
    request=RegisterSerializer,
    responses={
        200: SuccessResponseSerializer,
        400: ErrorResponseSerializer,
    },
    examples=[
        OpenApiExample(
            'Inscription réussie',
            description='Exemple d\'inscription réussie',
            value={'username': 'john_doe', 'password': 'monmotdepasse123'},
            request_only=True,
        ),
    ],
    tags=['Authentification']
)
@csrf_exempt
@api_view(['POST'])
def register(request):
    logger.info("=== REGISTER REQUEST ===")
    logger.info(f"Request method: {request.method}")
    logger.info(f"Content-Type: {request.META.get('CONTENT_TYPE', 'N/A')}")
    logger.info(f"Origin: {request.META.get('HTTP_ORIGIN', 'N/A')}")
    
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        logger.info(f"Registration attempt for username: {username}")
        
        if not username or not password:
            logger.warning(f"Missing credentials - username: {bool(username)}, password: {bool(password)}")
            return JsonResponse({
                'success': False,
                'error': 'Username and password are required'
            }, status=400)
        
        if User.objects.filter(username=username).exists():
            logger.warning(f"Registration failed - username '{username}' already exists")
            return JsonResponse({
                'success': False,
                'error': 'Username already exists'
            }, status=400)
        
        user = User.objects.create_user(username=username, password=password)
        logger.info(f"User '{username}' registered successfully with ID: {user.id}")
        return JsonResponse({'success': True})
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in register request: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON'
        }, status=400)
    except Exception as e:
        logger.error(f"Unexpected error in register: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@extend_schema(
    operation_id='login_user',
    summary='Connexion utilisateur',
    description='Authentifier un utilisateur et recevoir un token JWT.',
    request=LoginSerializer,
    responses={
        200: LoginResponseSerializer,
        400: ErrorResponseSerializer,
        401: ErrorResponseSerializer,
    },
    examples=[
        OpenApiExample(
            'Connexion réussie',
            description='Exemple de connexion réussie',
            value={'username': 'john_doe', 'password': 'monmotdepasse123'},
            request_only=True,
        ),
    ],
    tags=['Authentification']
)
@csrf_exempt
@api_view(['POST'])
def login(request):
    logger.info("=== LOGIN REQUEST ===")
    logger.info(f"Request method: {request.method}")
    logger.info(f"Content-Type: {request.META.get('CONTENT_TYPE', 'N/A')}")
    logger.info(f"Origin: {request.META.get('HTTP_ORIGIN', 'N/A')}")
    
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        logger.info(f"Login attempt for username: {username}")
        
        if not username or not password:
            logger.warning(f"Missing credentials - username: {bool(username)}, password: {bool(password)}")
            return JsonResponse({'error': 'Username and password are required'}, status=400)
        
        user = authenticate(username=username, password=password)
        if user:
            token = create_jwt_token(user)
            logger.info(f"Login successful for user '{username}' (ID: {user.id})")
            logger.debug(f"Generated JWT token: {token[:20]}...")
            return JsonResponse({'token': token})
        else:
            logger.warning(f"Login failed for username '{username}' - invalid credentials")
            return JsonResponse({'error': 'Invalid credentials'}, status=401)
            
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in login request: {e}")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error in login: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@extend_schema(
    operation_id='list_users',
    summary='Liste des utilisateurs',
    description='Récupérer la liste de tous les utilisateurs enregistrés.',
    responses={
        200: UsersResponseSerializer,
        401: ErrorResponseSerializer,
    },
    parameters=[
        OpenApiParameter(
            name='x-api-key',
            type=str,
            location=OpenApiParameter.HEADER,
            description='Token JWT d\'authentification',
            required=True
        )
    ],
    tags=['Utilisateurs']
)
@jwt_required
@api_view(['GET'])
def users(request):
    logger.info("=== USERS LIST REQUEST ===")
    logger.info(f"Request from user: {request.user.username} (ID: {request.user.id})")
    logger.info(f"Origin: {request.META.get('HTTP_ORIGIN', 'N/A')}")
    
    try:
        users_list = []
        all_users = User.objects.all()
        logger.info(f"Found {all_users.count()} users in database")
        
        for user in all_users:
            users_list.append({
                'id': user.id,
                'username': user.username
            })
            logger.debug(f"Added user to list: {user.username} (ID: {user.id})")
        
        logger.info(f"Returning {len(users_list)} users to client")
        return JsonResponse({'users': users_list})
    except Exception as e:
        logger.error(f"Error retrieving users list: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@extend_schema(
    operation_id='handle_messages',
    summary='Gestion des messages',
    description='Envoyer un nouveau message (POST) ou récupérer les messages (GET).',
    request={
        'application/json': SendMessageSerializer
    },
    responses={
        200: MessagesResponseSerializer,
        400: ErrorResponseSerializer,
        401: ErrorResponseSerializer,
    },
    parameters=[
        OpenApiParameter(
            name='x-api-key',
            type=str,
            location=OpenApiParameter.HEADER,
            description='Token JWT d\'authentification',
            required=True
        )
    ],
    examples=[
        OpenApiExample(
            'Message texte simple',
            description='Envoi d\'un message texte public',
            value={'content': 'Bonjour tout le monde!'},
            request_only=True,
        ),
        OpenApiExample(
            'Message privé',
            description='Envoi d\'un message privé à un utilisateur',
            value={'content': 'Message privé', 'to': 2},
            request_only=True,
        ),
        OpenApiExample(
            'Message avec image',
            description='Envoi d\'un message avec image',
            value={
                'content': 'Regardez cette image!',
                'image': {
                    'name': 'photo.png',
                    'content': 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=='
                }
            },
            request_only=True,
        ),
    ],
    tags=['Messages']
)
@csrf_exempt
@jwt_required
@api_view(['GET', 'POST'])
def messages_handler(request):
    logger.info(f"=== MESSAGES REQUEST ({request.method}) ===")
    logger.info(f"Request from user: {request.user.username} (ID: {request.user.id})")
    logger.info(f"Origin: {request.META.get('HTTP_ORIGIN', 'N/A')}")
    
    if request.method == 'POST':
        return send_message(request)
    elif request.method == 'GET':
        return get_messages(request)

def send_message(request):
    logger.info("--- SEND MESSAGE ---")
    
    try:
        data = json.loads(request.body)
        content = data.get('content')
        to_user_id = data.get('to')
        image_data = data.get('image')
        
        logger.info(f"Message content: {content[:50]}..." if len(content) > 50 else f"Message content: {content}")
        logger.info(f"Target user ID: {to_user_id}")
        logger.info(f"Has image: {bool(image_data)}")
        
        if not content:
            logger.warning("Message rejected - empty content")
            return JsonResponse({
                'success': False,
                'error': 'Content is required'
            }, status=400)
        
        message = Message(
            content=content,
            from_user=request.user
        )
        
        message_type = "public"
        if to_user_id:
            try:
                to_user = User.objects.get(id=to_user_id)
                message.to_user = to_user
                message_type = f"private to {to_user.username}"
                logger.info(f"Private message target: {to_user.username} (ID: {to_user.id})")
            except User.DoesNotExist:
                logger.warning(f"Recipient user not found: ID {to_user_id}")
                return JsonResponse({
                    'success': False,
                    'error': 'Recipient user not found'
                }, status=400)
        
        if image_data and isinstance(image_data, dict):
            image_name = image_data.get('name')
            image_content = image_data.get('content')
            
            if image_name and image_content:
                try:
                    logger.info(f"Processing image: {image_name} ({len(image_content)} chars base64)")
                    image_file = ContentFile(
                        base64.b64decode(image_content),
                        name=image_name
                    )
                    message.image = image_file
                    logger.info("Image processed successfully")
                except Exception as e:
                    logger.error(f"Image processing failed: {e}")
                    return JsonResponse({
                        'success': False,
                        'error': 'Invalid image data'
                    }, status=400)
        
        message.save()
        logger.info(f"Message saved successfully - ID: {message.id}, Type: {message_type}")
        return JsonResponse({'success': True})
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in send message: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON'
        }, status=400)
    except Exception as e:
        logger.error(f"Unexpected error in send message: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def get_messages(request):
    logger.info("--- GET MESSAGES ---")
    
    try:
        messages = Message.objects.filter(
            models.Q(from_user=request.user) |
            models.Q(to_user=request.user) |
            models.Q(to_user__isnull=True)
        ).order_by('-created_at')
        
        logger.info(f"Found {messages.count()} messages for user {request.user.username}")
        
        messages_list = []
        public_count = 0
        private_count = 0
        
        for message in messages:
            message_data = {
                'content': message.content,
                'from': {
                    'id': message.from_user.id,
                    'username': message.from_user.username
                }
            }
            
            if message.image:
                # Build the correct HTTPS URL for external access
                # Always use the external IP and HTTPS port for frontend compatibility
                external_ip = "10.111.46.149"  # Known external IP
                image_url = f"https://{external_ip}:8443{message.image.url}"
                
                message_data['image'] = image_url
                logger.debug(f"Message {message.id} has image: {message.image.name} -> {image_url}")
            
            if message.to_user:
                message_data['to'] = {
                    'id': message.to_user.id,
                    'username': message.to_user.username
                }
                private_count += 1
                logger.debug(f"Private message {message.id}: {message.from_user.username} -> {message.to_user.username}")
            else:
                public_count += 1
                logger.debug(f"Public message {message.id} from {message.from_user.username}")
            
            messages_list.append(message_data)
        
        logger.info(f"Returning {len(messages_list)} messages ({public_count} public, {private_count} private)")
        return JsonResponse({'messages': messages_list})
        
    except Exception as e:
        logger.error(f"Error retrieving messages: {e}")
        return JsonResponse({'error': str(e)}, status=500)