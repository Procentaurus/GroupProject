from pathlib import Path
from datetime import timedelta

from django.conf import settings

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = '78NwJjMS1M8Bg55/dV59ll/CK6dNm3KRl9WhLtW7pOyoSNfHQ4h+DEaDRjEEJgF' \
    + '9x6PtqphjTDlzLUJ1WetCF0uMk1K1qI4ePuQ0K+ydvM4oyZ7G9Lwjuqqgf5KMhRHpBvv8c' \
    + '8JCQdGEz+IENLf5V/VC43MPOjG72ju9rS+klWubXyY8CznZJk8Aupk6Q8/oRSp6zJY2iBo' \
    + 'T7yW7trv1j7F/jjrBiDmyM7Y+pa8IhvvSRoo8V3iUQURpv3KRmSmd8GVlwXubQdIna/GKA' \
    + 'rqyEz71/lkQQmRJDPNn1YzOY7+QyoDSOGftw78CpjxPaIvRRzGZb+7l4gL+vZNdT0gJ+k5' \
    + 'Wn0AVhaJ3JpX+qoJjX3A='

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Networking config
ALLOWED_HOSTS = ["*"]
CORS_ORIGIN_ALLOW_ALL = False
CORS_ORIGIN_WHITELIST = (
  'http://localhost:8080',   # adress of frontend application
)

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

ROOT_URLCONF = 'SocketComponent.urls'

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

WSGI_APPLICATION = 'SocketComponent.wsgi.application'
ASGI_APPLICATION = "SocketComponent.asgi.application"



##############################    REDIS SETTINGS    ############################
REDIS_LAYER_HOST = '127.0.0.1'
REDIS_LAYER_PORT = 6378
REDIS_LAYER_DB = 0

REDIS_SCHEDULER_HOST = '127.0.0.1'
REDIS_SCHEDULER_PORT = 6378
REDIS_SCHEDULER_DB = 1

REDIS_MESSAGING_HOST = '127.0.0.1'
REDIS_MESSAGING_PORT = 6378
REDIS_MESSAGING_DB = 2

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [(REDIS_LAYER_HOST, REDIS_LAYER_PORT, REDIS_LAYER_DB)],
        },
    },
}
################################################################################


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

######### Throttle rates Settings #########
GAMETOKEN_CREATE_THROTTLE_HOUR_RATE = '60/hour'

################################################################################

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'SocketDataBase',
        'USER': 'postgres_socket',
        'PASSWORD': 'postgres_socket',
        'HOST': 'localhost',
        'PORT': '5498',
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


STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
