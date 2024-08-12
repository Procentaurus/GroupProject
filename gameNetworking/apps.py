from django.apps import AppConfig
import threading


class GamenetworkingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gameNetworking'

    def ready(self):
        from .messager.scheduler import start_task_checker

        threading.Thread(target=start_task_checker, daemon=True).start()
