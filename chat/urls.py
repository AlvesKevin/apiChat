from django.urls import path
from . import views

urlpatterns = [
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    path('users', views.users, name='users'),
    path('messages', views.messages_handler, name='messages'),
]