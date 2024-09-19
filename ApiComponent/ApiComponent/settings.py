from pathlib import Path
from datetime import timedelta
import os

from django.conf import settings

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = '78NwJjMS1M8Bg55/dV59ll/CK6dNm3KRl9WhLtW7pOyoSNfHQ4h+DEaDRjEEJgF' \
    + '9x6PtqphjTDlzLUJ1WetCF0uMk1K1qI4ePuQ0K+ydvM4oyZ7G9Lwjuqqgf5KMhRHpBvv8c' \
    + '8JCQdGEz+IENLf5V/VC43MPOjG72ju9rS+klWubXyY8CznZJk8Aupk6Q8/oRSp6zJY2iBo' \
    + 'T7yW7trv1j7F/jjrBiDmyM7Y+pa8IhvvSRoo8V3iUQURpv3KRmSmd8GVlwXubQdIna/GKA' \
    + 'rqyEz71/lkQQmRJDPNn1YzOY7+QyoDSOGftw78CpjxPaIvRRzGZb+7l4gL+vZNdT0gJ+k5' \
    + 'Wn0AVhaJ3JpX+qoJjX3A='

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Networking config
ALLOWED_HOSTS = ["*"]
CORS_ORIGIN_ALLOW_ALL = False
CORS_ORIGIN_WHITELIST = (
  'http://localhost:8080',   # adress of frontend application
)
CSRF_TRUSTED_ORIGINS = ['http://localhost:8000']

INSTALLED_APPS = [
 
    'corsheaders', # used to enable communication between frontend and backend
    'rest_framework',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'gameApi.apps.GameapiConfig'
]

AUTH_USER_MODEL = "gameApi.MyUser"

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = 'ApiComponent.urls'

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

WSGI_APPLICATION = 'ApiComponent.wsgi.application'
ASGI_APPLICATION = "ApiComponent.asgi.application"



##############################    REDIS SETTINGS    ############################
REDIS_MESSAGING_HOST = 'redis'
REDIS_MESSAGING_PORT = 6379
REDIS_MESSAGING_DB = 2
################################################################################


#############################    GAME SETTINGS    ##############################

######### Channels names Settings #########
IN_GAME_STATUS_MESSAGING_CHANNEL_NAME = 'in_game_status_messaging_channel'
ARCHIVE_CREATION_MESSAGING_CHANNEL_NAME = 'archive_creation_messaging_channel'

######### Pagination sizes Settings #########
ARCHIVE_LIST_ENDPOINT_PAGE_SIZE = int(
    os.getenv('ARCHIVE_LIST_ENDPOINT_PAGE_SIZE', 150))
MYUSER_LIST_ENDPOINT_PAGE_SIZE = int(
    os.getenv('MYUSER_LIST_ENDPOINT_PAGE_SIZE', 50))

######### Throttle rates Settings #########
MYUSER_LIST_THROTTLE_MIN_RATE = os.getenv(
    'MYUSER_LIST_THROTTLE_MIN_RATE', '15') + '/min'
MYUSER_GET_THROTTLE_MIN_RATE = os.getenv(
    'MYUSER_GET_THROTTLE_MIN_RATE', '15') + '/min'
ARCHIVE_LIST_THROTTLE_MIN_RATE = os.getenv(
    'ARCHIVE_LIST_THROTTLE_MIN_RATE', '20') + '/min'
ARCHIVE_LIST_THROTTLE_DAY_RATE = os.getenv(
    'ARCHIVE_LIST_THROTTLE_DAY_RATE', '200') + '/day'
MYUSER_LIST_THROTTLE_DAY_RATE = os.getenv(
    'MYUSER_LIST_THROTTLE_DAY_RATE', '100') + '/day'
MYUSER_GET_THROTTLE_DAY_RATE = os.getenv(
    'MYUSER_GET_THROTTLE_DAY_RATE', '400') + '/day'
MYUSER_CREATE_THROTTLE_DAY_RATE = os.getenv(
    'MYUSER_CREATE_THROTTLE_DAY_RATE', '5') + '/day'
MYUSER_UPDATE_THROTTLE_DAY_RATE = os.getenv(
    'MYUSER_UPDATE_THROTTLE_DAY_RATE', '15') + '/day'
MYUSER_DELETE_THROTTLE_DAY_RATE = os.getenv(
    'MYUSER_DELETE_THROTTLE_DAY_RATE', '1') + '/day'
CUSTOMTOKEN_CREATE_THROTTLE_ANON_HOUR_RATE = os.getenv(
    'CUSTOMTOKEN_CREATE_THROTTLE_ANON_HOUR_RATE', '10') + '/hour'
CUSTOMTOKEN_CREATE_THROTTLE_HOUR_RATE = os.getenv(
    'CUSTOMTOKEN_CREATE_THROTTLE_HOUR_RATE', '2') + '/hour'
CUSTOMTOKEN_ROTATE_THROTTLE_HOUR_RATE = os.getenv(
    'CUSTOMTOKEN_ROTATE_THROTTLE_HOUR_RATE', '5') + '/hour'
CUSTOMTOKEN_ROTATE_THROTTLE_DAY_RATE = os.getenv(
    'CUSTOMTOKEN_ROTATE_THROTTLE_DAY_RATE', '40') + '/day'
################################################################################

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=int(os.getenv('ACCESS_TOKEN_LIFETIME', 10))),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        minutes=int(os.getenv('REFRESH_TOKEN_LIFETIME', 120))),
    "UPDATE_LAST_LOGIN": True,
    'ROTATE_REFRESH_TOKENS': True,

    "ALGORITHM": "HS256",
    "SIGNING_KEY": settings.SECRET_KEY,
    "ISSUER": "ProcentaurusSystems",

    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",

    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",

    "JTI_CLAIM": "jti"
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTRESQL_DB_NAME'),
        'USER': os.getenv('POSTRESQL_USER'),
        'PASSWORD':os.getenv('POSTRESQL_PASSWORD'),
        'HOST': 'db_api',
        'PORT': '5432',
    }
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
         'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'myuser_list_throttle_min_rate': MYUSER_LIST_THROTTLE_MIN_RATE,
        'myuser_get_throttle_min_rate': MYUSER_GET_THROTTLE_MIN_RATE,
        'archive_list_throttle_min_rate': ARCHIVE_LIST_THROTTLE_MIN_RATE,
        'archive_list_throttle_day_rate': ARCHIVE_LIST_THROTTLE_DAY_RATE,
        'myuser_list_throttle_day_rate': MYUSER_LIST_THROTTLE_DAY_RATE,
        'myuser_get_throttle_day_rate': MYUSER_GET_THROTTLE_DAY_RATE,
        'myuser_create_throttle_day_rate': MYUSER_CREATE_THROTTLE_DAY_RATE,
        'myuser_update_throttle_day_rate': MYUSER_UPDATE_THROTTLE_DAY_RATE,
        'myuser_delete_throttle_day_rate': MYUSER_DELETE_THROTTLE_DAY_RATE,
        'customtoken_create_throttle_anon_hour_rate': CUSTOMTOKEN_CREATE_THROTTLE_ANON_HOUR_RATE,
        'customtoken_create_throttle_hour_rate': CUSTOMTOKEN_CREATE_THROTTLE_HOUR_RATE,
        'customtoken_rotate_throttle_hour_rate': CUSTOMTOKEN_ROTATE_THROTTLE_HOUR_RATE,
        'customtoken_rotate_throttle_day_rate': CUSTOMTOKEN_ROTATE_THROTTLE_DAY_RATE
    }
}

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


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STATIC_URL = '/static/api/'
MEDIA_URL = '/media/api/'

STATIC_ROOT = '/var/www/api/static/'
MEDIA_ROOT = '/var/www/api/media/'
