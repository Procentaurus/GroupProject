from pathlib import Path
from datetime import timedelta

from django.conf import settings

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = '78NwJjMS1M8Bg55/dV59eS/CK6dNm3KRl9WhLtW7pOyoSNfHQ4h+DEaDRjEEJgF' \
    + '9x6PtqphjTDlzLUJ1WetCF4uMk1K1qI4ePuQ0K+ydvM4oyZ7G9Lwjuqqgf5KMhRHpBvv8c' \
    + '7JCQdGEz+IENLf5V/VC43MPOjG72ju9rS+klWubXyY8CznZJk8Aupk6Q8/oRSp6zJY2iBo' \
    + 'T7yW7trv1j7F/jjrBiDmyM7Y+pa8IhvvSRsb8V3iUQURpv3KRmSmd8GVlwXubQdIna/GKA' \
    + 'rqyEz71/lkQQmRJDPNn1YzOY7+QyoDSOGftw78CpjxPaKvRRzGZb+7l4gL+vZNdT0gJ+k5' \
    + 'Wn0AVhaJ3J4X+qoJjX3A='
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

    'daphne', # used for running asgi server       
    'corsheaders', # used to enable communication between frontend and backend

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



#################################    REDIS    #################################
REDIS_LAYER_HOST = '127.0.0.1'
REDIS_LAYER_PORT = 6379
REDIS_LAYER_DB = 0

REDIS_SCHEDULER_HOST = '127.0.0.1'
REDIS_SCHEDULER_PORT = 6379
REDIS_SCHEDULER_DB = 1

REDIS_MESSAGING_HOST = '127.0.0.1'
REDIS_MESSAGING_PORT = 6379
REDIS_MESSAGING_DB = 2

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [(REDIS_LAYER_HOST, REDIS_LAYER_PORT, REDIS_LAYER_DB)],
        },
    },
}


#############################    GAME SETTINGS    ##############################

######### Timeouts Settings #########
ACTION_MOVE_TIMEOUT = 30
REACTION_MOVE_TIMEOUT = 60
HUB_STAGE_TIMEOUT = 60
DELETE_GAME_STATE_TIMEOUT = 10
DELETE_GAME_TIMEOUT = 100
REJOIN_TIMEOUT = 30           # !!! Must be smaller than DELETE_GAME_TIMEOUT !!!

TIMEOUT_MODULE = 'gameNetworking.messager.tasks'

ACTION_MOVE_FUNC_NAME = 'limit_action_time'
REACTION_MOVE_FUNC_NAME = 'limit_reaction_time'
HUB_STAGE_FUNC_NAME = 'limit_hub_time'
DELETE_GAME_STATE_FUNC_NAME = 'limit_game_state_lifetime'
DELETE_GAME_FUNC_NAME = 'limit_game_data_lifetime'
REJOIN_FUNC_NAME = 'limit_opponent_rejoin_time'

ACTION_MOVE_TIMEOUT_FUNC = TIMEOUT_MODULE + '.' + ACTION_MOVE_FUNC_NAME
REACTION_MOVE_TIMEOUT_FUNC = TIMEOUT_MODULE + '.' + REACTION_MOVE_FUNC_NAME
HUB_STAGE_TIMEOUT_FUNC = TIMEOUT_MODULE + '.' + HUB_STAGE_FUNC_NAME
DELETE_GAME_STATE_TIMEOUT_FUNC = TIMEOUT_MODULE + '.' + DELETE_GAME_STATE_FUNC_NAME
DELETE_GAME_TIMEOUT_FUNC = TIMEOUT_MODULE + '.' + DELETE_GAME_FUNC_NAME
REJOIN_TIMEOUT_FUNC = TIMEOUT_MODULE + '.' + REJOIN_FUNC_NAME

######### Gameplay Settings #########
INIT_MOVES_PER_CLASH = 1
MAX_MOVES_PER_CLASH = 3
TURNS_BETWEEN_NUM_MOVES_INC = 5

INIT_A_CARDS_NUMBER = 2
INIT_R_CARDS_NUMBER = 5
REROLL_PRICE_INITIAL_VALUE = 30
REROLL_PRICE_INCREASE_VALUE = 10
MORALE_INITIAL_VALUE = 100
MONEY_INITIAL_VALUE = 500

######### Channels names Settings #########
DELAYED_GAME_TASKS_SORTED_SET_NAME = 'tasks'
GAMES_STATES_QUEUE_NAME = 'games_states'
TASK_CALLBACK_FUNCTIONS_QUEUE_NAME = 'task_funcs'
IN_GAME_STATUS_MESSAGING_CHANNEL_NAME = 'in_game_status_messaging_channel'
ARCHIVE_CREATION_MESSAGING_CHANNEL_NAME = 'archive_creation_messaging_channel'

################################################################################


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
    "UPDATE_LAST_LOGIN": True,

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

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
