import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me-in-production')

DEBUG = config('DEBUG', default=True, cast=bool)

# Allow all hosts for external access
ALLOWED_HOSTS = ['*']

# Force HTTPS URLs for media files when behind nginx proxy
USE_TLS = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
FORCE_SCRIPT_NAME = None

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'chat',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # 'corsheaders.middleware.CorsMiddleware',  # Disabled - nginx handles CORS
    'chat.middleware.RequestLoggingMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'chatbot_api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'chatbot_api.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='chatbot'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='postgres'),
        'HOST': config('DB_HOST', default='db'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

AUTH_USER_MODEL = 'chat.User'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': [],
}

JWT_SECRET_KEY = config('JWT_SECRET_KEY', default='your-jwt-secret-key-change-in-production')

# CORS Configuration - Handled by nginx proxy to avoid conflicts
# CORS_ALLOW_ALL_ORIGINS = True
# CORS_ALLOW_CREDENTIALS = True

# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000",
#     "http://127.0.0.1:3000",
#     "https://demo-chat-0b57ce.gitlab.io",
# ]

# CORS_ALLOW_HEADERS = [
#     'accept',
#     'accept-encoding',
#     'authorization',
#     'content-type',
#     'dnt',
#     'origin',
#     'user-agent',
#     'x-csrftoken',
#     'x-requested-with',
#     'x-api-key',
# ]

# CORS_ALLOW_METHODS = [
#     'DELETE',
#     'GET',
#     'OPTIONS',
#     'PATCH',
#     'POST',
#     'PUT',
# ]

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {asctime} {name}: {message}',
            'style': '{',
        },
        'api': {
            'format': '[API] {asctime} {name} - {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'api_console': {
            'class': 'logging.StreamHandler',
            'formatter': 'api',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': '/app/logs/api.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'chat': {
            'handlers': ['api_console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'chat.views': {
            'handlers': ['api_console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'chat.authentication': {
            'handlers': ['api_console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'api_requests': {
            'handlers': ['api_console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}