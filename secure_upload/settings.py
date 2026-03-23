import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "dev-insecure-key"
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "uploads",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = "secure_upload.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "uploads" / "templates"],
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

WSGI_APPLICATION = "secure_upload.wsgi.application"
ASGI_APPLICATION = "secure_upload.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SECURE_CONTENT_TYPE_NOSNIFF = True

FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024

UPLOAD_ALLOWED_EXTENSIONS = ["pdf", "png", "jpg", "jpeg", "gif", "bmp", "webp"]
UPLOAD_ALLOWED_MIME_TYPES = ["application/pdf", "image/png", "image/jpeg", "image/gif", "image/bmp", "image/webp"]
UPLOAD_MAX_SIZE = 5 * 1024 * 1024

CLAMAV_HOST = os.environ.get("CLAMAV_HOST", "127.0.0.1")
CLAMAV_PORT = int(os.environ.get("CLAMAV_PORT", "3310"))

SCAN_STRICT = os.environ.get("SCAN_STRICT", "0") == "1"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "upload_file": {
            "class": "logging.FileHandler",
            "filename": str(BASE_DIR / "upload_audit.log"),
            "level": "INFO",
        },
        "console": {"class": "logging.StreamHandler"},
    },
    "loggers": {
        "uploads": {
            "handlers": ["upload_file", "console"],
            "level": "INFO",
            "propagate": False,
        }
    },
}

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/uploads/"
LOGOUT_REDIRECT_URL = "/"
