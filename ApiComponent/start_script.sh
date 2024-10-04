#!/bin/bash

check_redis() {
    while ! redis-cli -h redis -p 6379 ping > /dev/null 2>&1; do
        echo "Waiting for Redis..."
        sleep 1
    done
    echo "Redis is up"
}

check_postgres() {
    while ! pg_isready -h db_api -p 5432 -U postgres_api > /dev/null 2>&1; do
        echo "Waiting for PostgreSQL..."
        sleep 1
    done
    echo "PostgreSQL is up"
}

check_redis
check_postgres

echo "Preparing database migrations"
python manage.py makemigrations gameApi

echo "Running migrations"
python manage.py migrate

echo "Collecting all static data"
python manage.py collectstatic

echo "Create admin account"
python manage.py create_admin

echo "Starting production server"
python manage.py run_messaging &
python manage.py runserver 0.0.0.0:8000
