from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Message

admin.site.register(User, UserAdmin)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['content', 'from_user', 'to_user', 'created_at']
    list_filter = ['created_at', 'from_user', 'to_user']
    search_fields = ['content', 'from_user__username', 'to_user__username']