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

### Stage 2: Final runtime environment ###
FROM python:3.9-slim

RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN mkdir -p /var/www/api/static/ /var/www/api/media/

COPY --from=dependencies /wheels /wheels

RUN pip install --no-cache /wheels/*

COPY . /app/

RUN chown -R appuser:appuser /app
RUN chown -R appuser:appuser /var/www/api/static/ /var/www/api/media/

WORKDIR /app

ENV DJANGO_SETTINGS_MODULE=ApiComponent.settings

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

ENV POSTRESQL_USER=postgres_api
ENV POSTRESQL_PASSWORD=postgres_api
ENV POSTRESQL_DB_NAME=ApiDataBase

######## Pagination sizes Settings ########
ENV ARCHIVE_LIST_ENDPOINT_PAGE_SIZE=150
ENV MYUSER_LIST_ENDPOINT_PAGE_SIZE=50

######### Throttle rates Settings #########
ENV MYUSER_LIST_THROTTLE_MIN_RATE=15
ENV MYUSER_GET_THROTTLE_MIN_RATE=15
ENV ARCHIVE_LIST_THROTTLE_MIN_RATE=20
ENV ARCHIVE_LIST_THROTTLE_DAY_RATE=200
ENV MYUSER_LIST_THROTTLE_DAY_RATE=100
ENV MYUSER_GET_THROTTLE_DAY_RATE=400
ENV MYUSER_CREATE_THROTTLE_DAY_RATE=5
ENV MYUSER_UPDATE_THROTTLE_DAY_RATE=15
ENV MYUSER_DELETE_THROTTLE_DAY_RATE=1
ENV CUSTOMTOKEN_CREATE_THROTTLE_ANON_HOUR_RATE=10
ENV CUSTOMTOKEN_CREATE_THROTTLE_HOUR_RATE=2
ENV CUSTOMTOKEN_ROTATE_THROTTLE_HOUR_RATE=5
ENV CUSTOMTOKEN_ROTATE_THROTTLE_DAY_RATE=40

######### JWT Settings #########
ENV ACCESS_TOKEN_LIFETIME=10
ENV REFRESH_TOKEN_LIFETIME=120

ENTRYPOINT ["/bin/bash", "/app/start_script.sh"]
