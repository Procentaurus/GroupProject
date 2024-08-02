from django.conf import settings

from customUser.models.queries import create_game_archive

from ...models.queries import get_game, delete_game, delete_game_user
from ...scheduler.scheduler import add_delayed_task, remove_delayed_task


class Disconnector:

    def __init__(self, consumer):
        self._consumer = consumer

    async def disconnect(self):
        game = self._consumer.get_game()
        if self._consumer.closed_after_disconnect():
            await self._consumer.refresh_game()
            player = self._consumer.get_game_user()
            game = self._consumer.get_game()
            if game:
                await player.backup(self._consumer)
                if not game.is_backuped:
                    await self._consumer.send_message_to_opponent(
                        {}, "opponent_disconnect"
                    )
                    await game.backup(self._consumer)
                    self._remove_all_gameplay_tasks()
                    add_delayed_task(
                        f'limit_game_data_lifetime_{game.id}',
                        settings.DELETE_GAME_TIMEOUT,
                        settings.DELETE_GAME_TIMEOUT_FUNC
                    )
            else:
                await delete_game_user(player.id)
            return
        winner = self._consumer.get_winner()
        await self._consumer.send_message_to_opponent(
            {"winner" : winner},
            "game_end"
        )
        await create_game_archive(game, winner)
        await self._remove_player_from_group(game.id)
        await delete_game(game.id)
        self._remove_all_gameplay_tasks()

    async def _remove_player_from_group(self, game_id):
        await self._consumer.channel_layer.group_discard(
            f"game_{game_id}", self._consumer.channel_name)

    def _remove_all_gameplay_tasks(self):
        g_u_id = self._consumer.get_game_user().id
        opp_id = self._consumer.get_opponent().id
        remove_delayed_task(f'limit_action_time_{g_u_id}')
        remove_delayed_task(f'limit_action_time_{opp_id}')
        remove_delayed_task(f'limit_reaction_time_{g_u_id}')
        remove_delayed_task(f'limit_reaction_time_{opp_id}')
        remove_delayed_task(f'limit_hub_time_{g_u_id}')
        remove_delayed_task(f'limit_hub_time_{opp_id}')
        remove_delayed_task(f'limit_opponent_rejoin_time_{g_u_id}')
