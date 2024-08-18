from WebGame.loggers import get_server_logger

import threading
from django.apps import AppConfig


logger = get_server_logger()


class GamenetworkingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gameNetworking'

    def ready(self):
        from .messager.scheduler import start_task_checker

        threading.Thread(target=start_task_checker, daemon=True).start()
        logger.info("Thread handling game tasks has started")
