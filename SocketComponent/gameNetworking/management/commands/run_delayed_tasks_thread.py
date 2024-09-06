import redis
import threading
from django.conf import settings
from django.core.management.base import BaseCommand

from SocketComponent.loggers import get_server_logger

from ...messager.scheduler import start_task_checker


redis_client = redis.StrictRedis(
    host=settings.REDIS_SCHEDULER_HOST,
    port=settings.REDIS_SCHEDULER_PORT,
    db=settings.REDIS_SCHEDULER_DB
)
logger = get_server_logger()


class Command(BaseCommand):
    help = 'Start threads to provide Redis delayed game tasks handling'

    def handle(self, *args, **kwargs):
        tasks_thread = threading.Thread(
            target=start_task_checker)

        tasks_thread.start()
        logger.info("Thread handling game tasks has started")
        tasks_thread.join()
