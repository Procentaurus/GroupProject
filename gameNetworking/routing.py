from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/game/(?P<conflict_side>\w+)/$", consumers.QueueConsumer.as_asgi()),
]