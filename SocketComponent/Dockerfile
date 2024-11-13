### Stage 1: Build environment ###
FROM python:3.9-slim AS dependencies

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && apt-get clean

WORKDIR /app

RUN pip install --upgrade pip

COPY requirements.txt /app/

# Install Python dependencies (building wheels in this stage)
RUN pip wheel --no-cache-dir --no-deps -r requirements.txt -w /wheels

### Stage 2: Copy files ###
FROM alpine:3.20.3 AS files

COPY . /app/

RUN rm -r ./app/static

COPY ./static /static/

### Stage 3: Final runtime environment ###
FROM python:3.9-slim

RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN mkdir -p /var/www/socket/static/ /var/www/socket/media/

COPY --from=dependencies /wheels /wheels
COPY --from=files /static /var/www/socket/media
COPY --from=files /app /app

RUN pip install --no-cache /wheels/*
RUN chown -R appuser:appuser /app
RUN chown -R appuser:appuser /var/www/socket/static/ /var/www/socket/media/

WORKDIR /app

ENV DJANGO_SETTINGS_MODULE=SocketComponent.settings

RUN chmod +x start_script.sh
RUN apt-get update
RUN apt-get install -y bash
RUN apt-get install -y redis-tools
RUN apt-get install -y postgresql-client

USER appuser

################ Auth data ################
ENV DJANGO_SUPERUSER_USERNAME=Procentaurus
ENV DJANGO_SUPERUSER_EMAIL=michalski.44@wp.pl
ENV DJANGO_SUPERUSER_PASSWORD=123456PIOTR

ENV POSTRESQL_USER=postgres_socket
ENV POSTRESQL_PASSWORD=postgres_socket
ENV POSTRESQL_DB_NAME=SocketDataBase

ENV SECRET_KEY=78NwJjMS1M8Bg55/dV59ll/CK6dNm3KRl9WhLtW7pOyoSNfHQ4h+DEaDRjEEJgF9x6PtqphjTDlzLUJ1WetCF0uMk1K1qI4ePuQ0K+ydvM4oyZ7G9Lwjuqqgf5KMhRHpBvv8c8JCQdGEz+IENLf5V/VC43MPOjG72ju9rS+klWubXyY8CznZJk8Aupk6Q8/oRSp6zJY2iBoT7yW7trv1j7F/jjrBiDmyM7Y+pa8IhvvSRoo8V3iUQURpv3KRmSmd8GVlwXubQdIna/GKArqyEz71/lkQQmRJDPNn1YzOY7+QyoDSOGftw78CpjxPaIvRRzGZb+7l4gL+vZNdT0gJ+k5Wn0AVhaJ3JpX+qoJjX3A=

############ Gameplay Settings ###########
ENV INIT_MOVES_PER_CLASH=1
ENV MAX_MOVES_PER_CLASH=3
ENV TURNS_BETWEEN_NUM_MOVES_INC=5
ENV INIT_A_CARDS_NUMBER=2
ENV INIT_R_CARDS_NUMBER=5
ENV REROLL_PRICE_INITIAL_VALUE=30
ENV REROLL_PRICE_INCREASE_VALUE=10
ENV MORALE_INITIAL_VALUE=100
ENV MONEY_INITIAL_VALUE=500

########### Timeouts Settings ###########
ENV ACTION_MOVE_TIMEOUT=3000000
ENV REACTION_MOVE_TIMEOUT=60000000
ENV HUB_STAGE_TIMEOUT=600000000
ENV DELETE_GAME_STATE_TIMEOUT=10000000
ENV DELETE_GAME_TIMEOUT=1000000000
# !!! Must be smaller than DELETE_GAME_TIMEOUT !!!
ENV REJOIN_TIMEOUT=30

############## JWT Settings #############
ENV ACCESS_TOKEN_LIFETIME=10
ENV REFRESH_TOKEN_LIFETIME=120

######## Throttle rates Settings ########
ENV GAMETOKEN_CREATE_THROTTLE_HOUR_RATE=60

ENTRYPOINT ["/bin/bash", "/app/start_script.sh"]
