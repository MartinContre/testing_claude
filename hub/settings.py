"""
Django settings for hub project.

Generated by 'django-admin startproject' using Django 5.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import os
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv
from google.cloud import secretmanager

load_dotenv()

API_VERSION = "v1"
SESSION_COOKIE_AGE = 3600
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")


def get_secret(secret_name):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{os.getenv('PROJECT_ID')}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/


# SECURITY WARNING: don't run with debug turned on in production!
SECRET_KEY = get_secret("DJANGO_SECRET_KEY")

DEBUG = not os.getenv("GAE_APPLICATION")
if DEBUG:
    EMAIL_HOST: str = "localhost"
    EMAIL_PORT: int = 1025
else:
    EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
    EMAIL_HOST = os.getenv("EMAIL_HOST") or "smtp.gmail.com"
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", "3305"))
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")


ALLOWED_HOSTS: list[str] = os.getenv("ALLOWED_HOSTS", "").split(",")


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "rest_framework.authtoken",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_filters",
    "drf_yasg",
    "authentication",
    "santander",
    "uvaq",
    "evoti",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "hub.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "client/templates", BASE_DIR / "emails/templates"],
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

LANGUAGE_CODE = "es-MX"

TIME_ZONE = "America/Mexico_City"

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = [
    BASE_DIR / "locale",
]
LANGUAGES = [
    ("es-MX", "Español de México"),
]


WSGI_APPLICATION = "hub.wsgi.application"

if not DEBUG:
    REST_FRAMEWORK = {
        "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
        "DEFAULT_AUTHENTICATION_CLASSES": [
            "authentication.hybrid_authentication.IdPAuthentication",
            "authentication.hybrid_authentication.HybridAuthentication",
            "authentication.web_auth.WebUploadAuthentication",
        ],
        "DEFAULT_PERMISSION_CLASSES": [
            "rest_framework.permissions.IsAuthenticated",
        ],
    }

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

if os.getenv("GAE_APPLICATION", None):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "HOST": get_secret("HOST-INSTANCE"),
            "USER": get_secret("USER-HUB-CONNECTIONS"),
            "PASSWORD": get_secret("PASS-USER-HUB"),
            "NAME": get_secret("HUB-CONNECTIONS-DB"),
        },
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "HOST": os.getenv("DB_HOST"),
            # "PORT": os.getenv("DB_PORT"),
            # "USER": get_secret("USER-HUB-CONNECTIONS"),
            # "PASSWORD": get_secret("PASS-USER-HUB"),
            # "NAME": get_secret("HUB-CONNECTIONS-DB"),
            "PORT": os.getenv("LOCAL_DB_PORT"),
            "USER": os.getenv("DB_USER"),
            "PASSWORD": os.getenv("DB_PASSWORD"),
            "NAME": os.getenv("DB_NAME"),
        },
    }
# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "es-MX"
TIME_ZONE = "America/Mexico_City"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_ROOT = "static"
STATIC_URL = "/static/"
STATICFILES_DIRS: list[Path] = []

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

GOOGLE_SECRET_KEY = get_secret("GOOGLE_SECRET_KEY")


# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "formatters": {
#         "verbose": {
#             "format": "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
#             "datefmt": "%d/%b/%Y %H:%M:%S",
#         },
#     },
#     "handlers": {
#         "console": {
#             "class": "logging.StreamHandler",
#             "formatter": "verbose",
#         },
#         "file": {
#             "class": "logging.FileHandler",
#             "filename": "debug.log",
#             "formatter": "verbose",
#         },
#     },
#     "root": {
#         "handlers": ["console", "file"],
#         "level": "DEBUG",
#     },
#     "loggers": {
#         "django": {
#             "handlers": ["console", "file"],
#             "level": "DEBUG",
#             "propagate": True,
#         },
#         "django.server": {
#             "handlers": ["console", "file"],
#             "level": "INFO",
#             "propagate": False,
#         },
#     },
# }

# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "handlers": {
#         "console": {
#             "class": "logging.StreamHandler",
#         },
#     },
#     "root": {
#         "handlers": ["console"],
#         "level": "DEBUG",
#     },
#     "loggers": {
#         "django": {
#             "handlers": ["console"],
#             "level": "DEBUG",
#             "propagate": True,
#         },
#     },
# }


# # APP engine

# APPENGINE_URL = os.getenv("APPENGINE_URL", default=None)
# SECONDARY_URL = os.getenv("SECONDARY_URL", default=None)

# if APPENGINE_URL:
#     if not urlparse(APPENGINE_URL).scheme:
#         APPENGINE_URL = f"https://{APPENGINE_URL}"
#     ALLOWED_HOSTS.append(urlparse(APPENGINE_URL).netloc)

# if SECONDARY_URL:
#     if not urlparse(SECONDARY_URL).scheme:
#         SECONDARY_URL = f"https://{SECONDARY_URL}"
#     ALLOWED_HOSTS.append(urlparse(SECONDARY_URL).netloc)

# else:
#     ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS")
#     if ALLOWED_HOSTS:
#         ALLOWED_HOSTS = ALLOWED_HOSTS.split(",")
#     else:
#         ALLOWED_HOSTS = []


# CSRF_TRUSTED_ORIGINS = []
# if APPENGINE_URL:
#     CSRF_TRUSTED_ORIGINS.append(APPENGINE_URL)
# if SECONDARY_URL:
#     CSRF_TRUSTED_ORIGINS.append(SECONDARY_URL)

# SECURE_SSL_REDIRECT = bool(APPENGINE_URL)


STAFF_UPLOAD_PASS = get_secret("STAFF_UPLOAD_PASS")
PROFESSOR_UPLOAD_PASS = get_secret("PROFESSOR_UPLOAD_PASS")
STUDENT_UPLOAD_PASS = get_secret("STUDENT_UPLOAD_PASS")
