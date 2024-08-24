from .models.queries import get_game_token


class GameAuthenticationTokenMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode("utf-8")
        token_string = query_string.split('=')[1]

        token = await get_game_token(token_string)
        if token is not None:
            scope['user_id'] = token.get_user_id()
            scope['token'] = token
            return await self.inner(scope, receive, send)
        else:
            return
