from django.conf import settings

from ...models.queries import get_game, delete_game
from ...scheduler.scheduler import add_delayed_task, remove_delayed_task


class Disconnector:

    def __init__(self, consumer):
        self._consumer = consumer

    async def disconnect(self):
        g_id = self._consumer.get_game_id()
        if self._consumer.closed_after_disconnect():
            g_u = self._consumer.get_game_user()
            await g_u.backup(self._consumer)

            game = await get_game(g_id)
            if not game.is_backuped:
                await self._consumer.send_message_to_opponent(
                    {}, "opponent_disconnect"
                )
                await game.backup(self._consumer)
                self.remove_all_gameplay_tasks()
                add_delayed_task(
                    f'limit_game_data_lifetime_{g_id}',
                    settings.DELETE_GAME_TIMEOUT,
                    settings.DELETE_GAME_TIMEOUT_FUNC
                )
            return
        await delete_game(g_id)
        await self._consumer.send_message_to_opponent(
                {"winner" : self._consumer.get_winner()}, "game_end")
        await self._remove_player_from_group(g_id)

    async def _remove_player_from_group(self, game_id):
        await self._consumer.channel_layer.group_discard(
            f"game_{game_id}", self._consumer.channel_name)

    def remove_all_gameplay_tasks(self):
        g_u_id = self._consumer.get_game_user().id
        opp_id = self._consumer.get_opponent().id
        remove_delayed_task(f'limit_action_time_{g_u_id}')
        remove_delayed_task(f'limit_action_time_{opp_id}')
        remove_delayed_task(f'limit_reaction_time_{g_u_id}')
        remove_delayed_task(f'limit_reaction_time_{opp_id}')
        remove_delayed_task(f'limit_hub_time_{g_u_id}')
        remove_delayed_task(f'limit_hub_time_{opp_id}')
