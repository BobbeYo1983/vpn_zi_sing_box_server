import os
from pathlib import Path


# Директории и пути
BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BASE_DIR.parent
DATA_DIR = PROJECT_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
SIGN_BOX_DIR = PROJECT_DIR / "sing-box"
SIGN_BOX_DIR.mkdir(parents=True, exist_ok=True)
SINGBOX_CONFIG_PATH = SIGN_BOX_DIR / "config.json"

# Переменные окружения
HOST_IP = os.environ.get("HOST_IP")

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
DEBUG = os.environ.get("DJANGO_DEBUG", "0") == "1"
LOG_LEVEL = os.environ.get("DJANGO_LOG_LEVEL")

SINGBOX_SERVER_PORT = int(os.environ["SINGBOX_SERVER_PORT"])
SINGBOX_SERVER_NAME = os.environ["SINGBOX_SERVER_NAME"]
SINGBOX_REALITY_PRIVATE_KEY = os.environ["SINGBOX_REALITY_PRIVATE_KEY"]
SINGBOX_REALITY_PUBLIC_KEY = os.environ["SINGBOX_REALITY_PUBLIC_KEY"]
SINGBOX_SHORT_ID = os.environ["SINGBOX_SHORT_ID"]

# После загрузки переменных окружения грузим настройки логирования
from utils.logging import LOGGING

ALLOWED_HOSTS = [
    #HOST_IP,
    "nginx",
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'vpn',
    'rest_framework',
]

MIDDLEWARE = [
    'utils.hmac.HMACAuthMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": DATA_DIR / "db.sqlite3",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = DATA_DIR / "staticfiles"

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}

# HMAC
HMAC_SERVICES = {
    "server": "hmac_secret_vpn_zi", #TODO подтягивать из .env
}

HMAC_MAX_SKEW = 60  # допустимое расхождение времени (сек) сервисов



