from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from gameNetworking.consumers import GameConsumer

application = ProtocolTypeRouter({
    "websocket": URLRouter([
        path("ws/game/<str:conflict_side>/", GameConsumer.as_asgi()),
    ]),
})