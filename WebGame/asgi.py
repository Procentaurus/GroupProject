import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from gameNetworking.middlewares import GameAuthenticationTokenMiddleware
from gameNetworking.routing import url_patterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WebGame.settings')

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": GameAuthenticationTokenMiddleware(
            URLRouter(url_patterns)
        ),
    }
)
