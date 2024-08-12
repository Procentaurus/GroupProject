from django.conf import settings

from ...enums import GameState
from ...models.queries import delete_game, delete_game_user
from ...messager.scheduler import *
from ...messager.publisher import create_archive, clear_in_game_status


class Disconnector:

    def __init__(self, consumer):
        self._consumer = consumer

    async def disconnect(self):
        player = self._consumer.get_game_user()
        if not self._is_game_initialised():
            await delete_game_user(player.id)
        else:
            await self._consumer.refresh_game()
            game = self._consumer.get_game()
            await self._clear_in_game_status(player)
            if self._consumer.is_closed_after_game_end():
                await self._disconnect_after_game_end(game)
            else:
                await self._disconnect_without_game_end(game, player)

    async def _disconnect_after_game_end(self, game):
        await self._remove_player_from_group(game.id)
        if check_game_state(str(game.id)) != GameState.DELETED:
            update_game_state(str(game.id), GameState.DELETED)
            winner = self._consumer.get_winner()
            await create_archive(game, winner)
            await delete_game(game.id)
            self._remove_all_gameplay_tasks()
            delete_player_states_queue(game.id)
            add_delayed_task(
                f'limit_game_state_lifetime_{game.id}',
                settings.DELETE_GAME_STATE_TIMEOUT,
                settings.DELETE_GAME_STATE_TIMEOUT_FUNC
            )

    async def _disconnect_without_game_end(self, game, player):
        if game:
            await player.backup(self._consumer)
            if check_game_state(str(game.id)) != GameState.BACKUPED:
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
        remove_delayed_task(f'limit_opponent_rejoin_time_{opp_id}')

    async def _clear_in_game_status(self, player):
        clear_in_game_status(str(player.user_id))

    def _is_game_initialised(self):
        game = self._consumer.get_game()
        return True if game is not None else False
