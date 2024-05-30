from django.conf import settings

from ...models.queries import get_game
from ...scheduler.scheduler import add_delayed_task


class Disconnector:

    def __init__(self, consumer):
        self._consumer = consumer

    async def disconnect(self):
        g_id = self._consumer.get_game_id()
        game = await get_game(g_id)
        if game is not None:
            await self._send_game_end_info_to_opponent()
            add_delayed_task(
                f'limit_game_data_lifetime{g_id}',
                settings.DELETE_GAME_TIMEOUT,
                settings.DELETE_GAME_TIMEOUT_FUNC
            )
        await self._remove_player_from_group(g_id)
 
    async def _send_game_end_info_to_opponent(self):
        w = self._consumer.get_winner()
        if not self._consumer.get_closure_from_user_side():
            await self._consumer.send_message_to_opponent(
                {"winner" : w}, "game_end")
        else:
            await self._consumer.send_message_to_opponent(
                {"winner" : w, "after_disconnect" : True},
                "game_end"
            )

    async def _remove_player_from_group(self, game_id):
        await self._consumer.channel_layer.group_discard(
            f"game_{game_id}", self._consumer.channel_name)
