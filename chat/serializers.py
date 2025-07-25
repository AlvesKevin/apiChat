from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Message

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Serializer pour les informations utilisateur"""
    class Meta:
        model = User
        fields = ['id', 'username']

class RegisterSerializer(serializers.Serializer):
    """Serializer pour l'inscription d'un nouvel utilisateur"""
    username = serializers.CharField(max_length=150, help_text="Nom d'utilisateur unique")
    password = serializers.CharField(write_only=True, help_text="Mot de passe")

class LoginSerializer(serializers.Serializer):
    """Serializer pour la connexion utilisateur"""
    username = serializers.CharField(max_length=150, help_text="Nom d'utilisateur")
    password = serializers.CharField(write_only=True, help_text="Mot de passe")

class LoginResponseSerializer(serializers.Serializer):
    """Serializer pour la réponse de connexion"""
    token = serializers.CharField(help_text="Token JWT à utiliser dans l'en-tête x-api-key")

class MessageImageSerializer(serializers.Serializer):
    """Serializer pour les images dans les messages"""
    name = serializers.CharField(help_text="Nom du fichier image")
    content = serializers.CharField(help_text="Contenu de l'image encodé en base64")

class SendMessageSerializer(serializers.Serializer):
    """Serializer pour l'envoi de messages"""
    content = serializers.CharField(help_text="Contenu du message")
    to = serializers.IntegerField(required=False, help_text="ID de l'utilisateur destinataire (optionnel pour message public)")
    image = MessageImageSerializer(required=False, help_text="Image optionnelle")

class MessageResponseSerializer(serializers.Serializer):
    """Serializer pour les messages retournés"""
    content = serializers.CharField(help_text="Contenu du message")
    from_user = UserSerializer(source='from', help_text="Expéditeur du message")
    to_user = UserSerializer(source='to', required=False, help_text="Destinataire du message (null pour message public)")
    image = serializers.URLField(required=False, help_text="URL de l'image si présente")
    created_at = serializers.DateTimeField(help_text="Date de création du message")

class UsersResponseSerializer(serializers.Serializer):
    """Serializer pour la liste des utilisateurs"""
    users = UserSerializer(many=True, help_text="Liste de tous les utilisateurs")

class MessagesResponseSerializer(serializers.Serializer):
    """Serializer pour la liste des messages"""
    messages = MessageResponseSerializer(many=True, help_text="Liste des messages accessibles à l'utilisateur")

class SuccessResponseSerializer(serializers.Serializer):
    """Serializer pour les réponses de succès"""
    success = serializers.BooleanField(help_text="Indique si l'opération a réussi")

class ErrorResponseSerializer(serializers.Serializer):
    """Serializer pour les réponses d'erreur"""
    error = serializers.CharField(help_text="Message d'erreur")
    success = serializers.BooleanField(default=False, help_text="Indique que l'opération a échoué")