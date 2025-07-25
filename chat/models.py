from django.db import models
from django.contrib.auth.models import AbstractUser
import os
import uuid

class User(AbstractUser):
    pass

def upload_to(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('images/', filename)

class Message(models.Model):
    content = models.TextField()
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', null=True, blank=True)
    image = models.ImageField(upload_to=upload_to, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']