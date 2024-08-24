from django.urls import re_path

from .consumers import GameConsumer


url_patterns = [
    re_path(r'^ws/game/(?P<conflict_side>\w+)/$', GameConsumer.as_asgi()),
]
