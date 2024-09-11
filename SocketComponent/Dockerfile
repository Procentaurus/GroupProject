### Stage 1: Build environment ###
FROM python:3.9-slim AS builder

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

### Stage 2: Final runtime environment ###
FROM python:3.9-slim

RUN groupadd -r appuser && useradd -r -g appuser appuser

COPY --from=builder /wheels /wheels

RUN pip install --no-cache /wheels/*

COPY . /app/

RUN chown -R appuser:appuser /app

WORKDIR /app

ENV DJANGO_SETTINGS_MODULE=SocketComponent.settings

RUN chmod +x start_script.sh
RUN apt-get update
RUN apt-get install -y bash
RUN apt-get install -y redis-tools
RUN apt-get install -y postgresql-client

USER appuser

ENV DJANGO_SUPERUSER_USERNAME=Procentaurus
ENV DJANGO_SUPERUSER_EMAIL=michalski.44@wp.pl
ENV DJANGO_SUPERUSER_PASSWORD=123456PIOTR

######### Gameplay Settings #########
ENV INIT_MOVES_PER_CLASH=1
ENV MAX_MOVES_PER_CLASH=3
ENV TURNS_BETWEEN_NUM_MOVES_INC=5
ENV INIT_A_CARDS_NUMBER=2
ENV INIT_R_CARDS_NUMBER=5
ENV REROLL_PRICE_INITIAL_VALUE=30
ENV REROLL_PRICE_INCREASE_VALUE=10
ENV MORALE_INITIAL_VALUE=100
ENV MONEY_INITIAL_VALUE=500

######### Timeouts Settings #########
ENV ACTION_MOVE_TIMEOUT=30
ENV REACTION_MOVE_TIMEOUT=60
ENV HUB_STAGE_TIMEOUT=60
ENV DELETE_GAME_STATE_TIMEOUT=10
ENV DELETE_GAME_TIMEOUT=100
# !!! Must be smaller than DELETE_GAME_TIMEOUT !!!
ENV REJOIN_TIMEOUT=30

######### JWT Settings #########
ENV ACCESS_TOKEN_LIFETIME=10
ENV REFRESH_TOKEN_LIFETIME=120

######### Throttle rates Settings #########
ENV GAMETOKEN_CREATE_THROTTLE_HOUR_RATE=60

ENTRYPOINT ["/bin/bash", "/app/start_script.sh"]
