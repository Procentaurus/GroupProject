from django.apps import AppConfig


class GamenetworkingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gameNetworking'

    # This starts the task checker thread when the app is ready
    def ready(self):
        from .scheduler import scheduler
