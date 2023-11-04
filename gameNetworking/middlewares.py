from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

from .queries import *

class GameAuthenticationTokenMiddleware:
    def __init__(self, inner):
        self.inner = inner

class GameAuthenticationTokenMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):

        query_string = scope.get("query_string", b"").decode("utf-8")
        token_string = query_string.split('=')[1]

        token = await get_token(token_string)
        user = await get_game_user(token_string)
        
        if token:
            scope['user'] = user
            scope['token'] = token
            scope['access_granted'] = True
        else:
            scope['access_granted'] = False
            
        return await self.inner(scope, receive, send)