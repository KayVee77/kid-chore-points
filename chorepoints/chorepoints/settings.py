from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'dev-insecure-key'
DEBUG = True
ALLOWED_HOSTS: list[str] = ['localhost', '127.0.0.1', '192.168.0.35', '*']  # Allow access from local network

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',  # For HTTPS runserver_plus
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # Add for i18n support
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'chorepoints.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'core' / 'templates'],
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

WSGI_APPLICATION = 'chorepoints.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = []  # Simplified for local MVP

LANGUAGE_CODE = 'lt'
TIME_ZONE = 'Europe/Vilnius'  # Lithuanian timezone
USE_I18N = True
USE_L10N = True  # Use localized formatting
USE_TZ = True

# Supported languages
LANGUAGES = [
    ('lt', 'Lietuvių'),
    ('en', 'English'),
]

# Path for locale files
LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # For collectstatic
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# After any Django auth logout (including admin) go to landing page
LOGOUT_REDIRECT_URL = '/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Session Security Settings
SESSION_COOKIE_AGE = 3600  # 1 hour (in seconds)
SESSION_SAVE_EVERY_REQUEST = False  # Only save when modified
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Clear session when browser closes
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookie
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
