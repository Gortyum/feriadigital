"""
Django settings for proyectoferiadigital project.
Configurado para desarrollo local seguro (HTTP).
"""

from pathlib import Path
from dotenv import load_dotenv
import os

# --- Cargar variables del archivo .env ---
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

OPENWEATHERMAP_API_KEY = os.getenv('OPENWEATHERMAP_API_KEY', 'tu_api_key_aqui')
WEATHER_CACHE_TIMEOUT = 1800  # 30 minutos en segundos


# --- Configuración básica ---
SECRET_KEY = os.getenv("SECRET_KEY", "")  
DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", "localhost", "0.0.0.0", "192.168.56.1", "26.243.164.252","10.58.3.201"]

# --- Aplicaciones instaladas ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'appferiadigital',
]

# --- Middleware (mantiene CSRF, sesiones, etc.) ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # Protección CSRF activa
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'proyectoferiadigital.urls'

# --- Templates ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'appferiadigital' / 'templates'],
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

WSGI_APPLICATION = 'proyectoferiadigital.wsgi.application'

# --- Base de datos ---
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', ''),
        'NAME': os.getenv('DB_NAME', ''),
        'USER': os.getenv('DB_USER', ''),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', ''),
        'PORT': os.getenv('DB_PORT', ''),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# --- Validación de contraseñas ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- Internacionalización ---
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

# --- Archivos estáticos ---
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'appferiadigital' / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# --- Clave primaria por defecto ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Seguridad básica local ---
CSRF_COOKIE_SECURE = False     
SESSION_COOKIE_SECURE = False  
SECURE_SSL_REDIRECT = False    
SECURE_HSTS_SECONDS = 0        
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
