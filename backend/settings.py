# File: backend/settings.py

import os
from pathlib import Path
from datetime import timedelta

# ---------------------------
# Base Directory
# ---------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------
# Security
# ---------------------------
SECRET_KEY = '(lw)^mdqdt8g4#!t!@#-ml96&=@jclj&i&2h67!d8fwi_z8!@@'
DEBUG = True
ALLOWED_HOSTS = ['*']

# ---------------------------
# Installed Apps
# ---------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'accounts',  # تطبيق المستخدمين

    'attendance',  # تطبيق الحضور
    
    ]

# ---------------------------
# Middleware
# ---------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',       # يجب أن يكون قبل AuthenticationMiddleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',    # ضروري لتسجيل الدخول و admin
    'django.contrib.messages.middleware.MessageMiddleware',       # ضروري للـ admin messages
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ---------------------------
# URL Config
# ---------------------------
ROOT_URLCONF = 'backend.urls'

# ---------------------------
# Templates
# ---------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

# ---------------------------
# WSGI
# ---------------------------
WSGI_APPLICATION = 'backend.wsgi.application'

# ---------------------------
# Database (SQLite للتطوير المحلي)
# ---------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ---------------------------
# Password validation
# ---------------------------
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

# ---------------------------
# Internationalization
# ---------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ---------------------------
# Static & Media
# ---------------------------
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ---------------------------
# REST Framework + JWT
# ---------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# ---------------------------
# Custom User Model (إذا استعملت حسابات مخصصة)
# ---------------------------
AUTH_USER_MODEL = 'accounts.User'
