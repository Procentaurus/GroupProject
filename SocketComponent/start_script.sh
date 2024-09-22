#!/bin/bash

check_redis() {
    while ! redis-cli -h redis -p 6379 ping > /dev/null 2>&1; do
        echo "Waiting for Redis..."
        sleep 1
    done
    echo "Redis is up"
}

check_postgres() {
    while ! pg_isready -h db_socket -p 5432 -U postgres_socket > /dev/null 2>&1; do
        echo "Waiting for PostgreSQL..."
        sleep 1
    done
    echo "PostgreSQL is up"
}

check_redis
check_postgres

echo "Preparing database migrations"
python manage.py makemigrations gameNetworking
python manage.py makemigrations gameMechanics

echo "Running migrations"
python manage.py migrate

echo "Uploading cards to the database"
python manage.py loaddata gameMechanics/fixtures/cards.json

echo "Collecting all static data"
python manage.py collectstatic

echo "Create superuser account"
python manage.py create_admin

echo "Starting production server"
daphne -b 0.0.0.0 -p 8000 SocketComponent.asgi:application &
python manage.py run_delayed_tasks_thread
