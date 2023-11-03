from django.urls import re_path

from consumers import *

websocket_urlpatterns = [
    re_path(r'^ws/game/(?P<conflict_side>\w+)/$', GameConsumer.as_asgi()),
]