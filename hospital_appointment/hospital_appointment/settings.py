"""
Django settings for hospital_appointment project.

Generated by 'django-admin startproject' using Django 4.2.18.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-0u%pipcxfalfc$nfep$+@w@$b67)4m)sg_$18+-^(46217r3=j"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# ---------Security---------------------------------------------------------------
ALLOWED_HOSTS = ['*']
CORS_ALLOWED_ORIGINS: True

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://192.168.1.15:5173",
]
CORS_ALLOW_HEADERS = [
    'content-type',
    'authorization',  
    'x-api-key',  
    'accept',
    'origin',
    'x-custom-header',  
    'X-Frame-Options',  
    'x-frontend-host'
]
CORS_ORIGIN_WHITELIST = [
    'http://localhost:5173',  
    "http://192.168.1.15:5173",
    "http://0.0.0.0:8000", 
    "http://localhost:8000",
]

# session _key
SESSION_COOKIE_AGE = 3600  # Log out after 1 hr of inactivity (
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Log out when the browser closes

SESSION_COOKIE_SECURE = False  # Set to True if using HTTPS
SESSION_COOKIE_SAMESITE = 'Lax'  # For cross-site cookies
CSRF_COOKIE_SAMESITE = 'Lax'  # For CSRF cookies if using CSRF protection
CSRF_COOKIE_SECURE = False  # Set to True if using HTTPS

CSRF_COOKIE_HTTPONLY = True  # Recommended for security

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:8000", 
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8080",
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'corsheaders',
    'oauth2_provider',
    'rest_framework',
    'appointmentapp',
    'users',
    'drf_yasg',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    'whitenoise.middleware.WhiteNoiseMiddleware',
    "django.middleware.common.CommonMiddleware",
    'corsheaders.middleware.CorsMiddleware',
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    'oauth2_provider.middleware.OAuth2TokenMiddleware',
]

ROOT_URLCONF = "hospital_appointment.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "hospital_appointment.wsgi.application"
AUTH_USER_MODEL = "users.UserDetails"
LOGIN_URL = '/login'

# AUTHENTICATION_BACKENDS = [
#     'oauth2_provider.backends.OAuth2Backend',
# ]

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "appointment.db",
#     }
# }

# deployed database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
        'OPTIONS': {
            'sslmode': 'require',  # This enforces SSL encryption
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Africa/Nairobi"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# REST_FRAMEWORK= {
#     'DEFAULT_AUTHENTICATION_CLASSES': [
#         'rest_framework.authentication.BasicAuthentication',
#         'rest_framework.authentication.SessionAuthentication',
#     ]
# }

# Allow anyone
# REST_FRAMEWORK= {
#     'DEFAULT_AUTHENTICATION_CLASSES': [
#         'rest_framework.permission.AllowAny',
#     ]
# }

OAUTH2_PROVIDER = {
    'ACCESS_TOKEN_EXPIRE_SECONDS': 3600,  # Token expiry time (1 hour)
    'REFRESH_TOKEN_EXPIRE_SECONDS': 86400,  # Refresh token expiry time (1 day)
    'SCOPES': {
        'read': 'Read access',
        'write': 'Write access',
        'groups': 'Access to your groups'
    }
}



REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        # 'rest_framework.permissions.IsAuthenticated',
        'rest_framework.permissions.AllowAny',
    )
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


