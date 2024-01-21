from django.contrib.auth.models import AnonymousUser

from .mechanics.queries import *

class GameAuthenticationTokenMiddleware:
    def __init__(self, inner):
        self.inner = inner

class GameAuthenticationTokenMiddleware: # implementation of getting data about player's single-use token
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):

        query_string = scope.get("query_string", b"").decode("utf-8")
        token_string = query_string.split('=')[1]

        token = await get_game_token(token_string)
        user = token.get_game_user()
        
        scope['user'] = user
        scope['token'] = token
            
        return await self.inner(scope, receive, send)