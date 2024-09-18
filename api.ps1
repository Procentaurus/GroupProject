cd ApiComponent
venv\Scripts\activate
python manage.py makemigrations gameApi
python manage.py migrate
python manage.py runserver
