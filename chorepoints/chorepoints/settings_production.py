"""
Production settings for ChorePoints deployed on Azure App Service.
Imports from base settings.py and overrides for production.
"""
from .settings import *
import os

# Security Settings
DEBUG = False
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
ALLOWED_HOSTS = [
    os.environ.get('WEBSITE_HOSTNAME'),  # Azure provides this
    'chorepoints-app.azurewebsites.net',  # Your app URL
    '*.azurewebsites.net',
]

# Database Configuration (PostgreSQL on Azure)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': '5432',
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}

# Azure Storage for Static and Media Files
AZURE_ACCOUNT_NAME = os.environ.get('AZURE_ACCOUNT_NAME')
AZURE_ACCOUNT_KEY = os.environ.get('AZURE_ACCOUNT_KEY')

# Use custom storage backends to separate static and media containers
STATICFILES_STORAGE = 'chorepoints.storage_backends.AzureStaticStorage'
DEFAULT_FILE_STORAGE = 'chorepoints.storage_backends.AzureMediaStorage'

# Static files (CSS, JavaScript, Images)
STATIC_URL = f'https://{AZURE_ACCOUNT_NAME}.blob.core.windows.net/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files (uploads)
MEDIA_URL = f'https://{AZURE_ACCOUNT_NAME}.blob.core.windows.net/media/'

# Security Settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Session Security - Override dev settings for production
SESSION_COOKIE_AGE = 3600  # 1 hour session timeout
SESSION_SAVE_EVERY_REQUEST = False
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Require login after browser close
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# HTTPS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
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
    },
}
