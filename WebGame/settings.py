from pathlib import Path
from datetime import timedelta

from django.conf import settings

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# TODO docelowo 256 znaków lub więcej
SECRET_KEY = 'django-insecure-i_!*j@r%biv$jm@e1)^_uhnea8f3)c*7b!*z7&xqd8(oim-53v'
AES_IV = b"3)c*7b!*z7&xqd8("
AES_SECRET_KEY = b"qd8(oim-53v-i_!@r%biv$jm@e1)^_uh"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Networking config
ALLOWED_HOSTS = ["*"]
CORS_ORIGIN_ALLOW_ALL = False
CORS_ORIGIN_WHITELIST = (
  'http://localhost:8080',   # adress of frontend application
)

AUTH_USER_MODEL = "customUser.MyUser"

INSTALLED_APPS = [

    'daphne',           # used for running asgi server       
    'corsheaders',      # used for enabling communication between frontend and backend

    'rest_framework',
    'channels',  

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'gameNetworking.apps.GamenetworkingConfig',
    'gameMechanics.apps.GamemechanicsConfig',
    'gameApi.apps.GameapiConfig',
    'customUser.apps.CustomuserConfig',

]

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

ROOT_URLCONF = 'WebGame.urls'

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

WSGI_APPLICATION = 'WebGame.wsgi.application'
ASGI_APPLICATION = "WebGame.asgi.application"

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
         'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_THROTTLE_RATES':{
        # 'login':'3/min',
        # 'publication':'10/hour',
        # 'publicationAll': '1000/day',
        # 'comment': '30/hour',
        # 'text': '5/hour',
        # 'project':'10/day',
    }
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(minutes=90),
    "UPDATE_LAST_LOGIN": True,                         # updates last_login field in MyUser enyity after logging procerssing token

    "ALGORITHM": "HS256",                             # JWT-specific config
    "SIGNING_KEY": settings.SECRET_KEY,
    "ISSUER": "ProcentaurusSystems",

    "AUTH_HEADER_TYPES": ("Bearer",),                 # default SimpleJWTConfig
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",

    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",

    "JTI_CLAIM": "jti"
}


LOGGING = {
    'version': 1,
    "disable_existing_loggers": False,
    'formatters': {
        'main': {
            'format': '{asctime} {module} {levelname} {message}',
            'style': '{',
            'datefmt':'%H:%M:%S',
        }
    },
    'handlers': {
        'views': {
            'class': 'logging.FileHandler',
            'filename': 'logs/networking/views.log',  # Specified path
            'formatter' : 'main'
        },
        'consumers': {
            'class': 'logging.FileHandler',
            'filename': 'logs/networking/consumers.log',  # Specified path
            'formatter' : 'main',
        },
    },
    'loggers': {
        'gameNetworking.views': {  # Specified logger for module
            'handlers': ['views'],
            'level': 'DEBUG',
        },
        'gameNetworking.consumers': {  # Specified logger for module
            'handlers': ['consumers'],
            'level': 'DEBUG',
        },
    },
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'GameDataBase',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',  # Use 'db' if using Docker Compose
        'PORT': '5431',
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


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
