from datetime import datetime
import redis
from django.conf import settings
import json
import threading
from django.core.management.base import BaseCommand

from django.conf import settings
from ...models.my_user.my_user import MyUser
from ...models.game_archive.game_archive import GameArchive


redis_client = redis.StrictRedis(
    host=settings.REDIS_MESSAGING_HOST,
    port=settings.REDIS_MESSAGING_PORT,
    db=settings.REDIS_MESSAGING_DB
)


def handle_in_game_status_update_task(data):
    user = MyUser.objects.get(id=data.get('user_id'))
    user.in_game = bool(data.get('new_status'))
    user.save()

def handle_archive_creation_task(data):
    archive = GameArchive.objects.create(
        start_date=datetime.fromisoformat(data.get('start_datetime')).date(),
        start_time=datetime.fromisoformat(data.get('start_datetime')).time(),
        winner=data.get('winner'),
        teacher_player=MyUser.objects.get(id=data.get('teacher_id')),
        student_player=MyUser.objects.get(id=data.get('student_id')),
        length_in_sec=data.get('len_in_sec')
    )
    archive.save()


def listen_for_archive_creation_tasks():
    pubsub = redis_client.pubsub()
    pubsub.subscribe(settings.ARCHIVE_CREATION_MESSAGING_CHANNEL_NAME)

    for message in pubsub.listen():
        if message['type'] == 'message':
            data = json.loads(message['data'].decode('utf-8'))
            print(f"Received request for game_archive creation {data}")
            handle_archive_creation_task(data)

def listen_for_in_game_status_update_tasks():
    pubsub = redis_client.pubsub()
    pubsub.subscribe(settings.IN_GAME_STATUS_MESSAGING_CHANNEL_NAME)

    for message in pubsub.listen():
        if message['type'] == 'message':
            data = json.loads(message['data'].decode('utf-8'))
            print(f"Received request for user status update: {data}")
            handle_in_game_status_update_task(data)


class Command(BaseCommand):
    help = 'Start threads to provide Redis intermodule communication'

    def handle(self, *args, **kwargs):
        archive_thread = threading.Thread(
            target=listen_for_archive_creation_tasks)
        status_update_thread = threading.Thread(
            target=listen_for_in_game_status_update_tasks)

        archive_thread.start()
        status_update_thread.start()

        archive_thread.join()
        status_update_thread.join()
