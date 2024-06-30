from django.conf import settings

from ...models.queries import get_game
from ...scheduler.scheduler import add_delayed_task, remove_delayed_task


class Disconnector:

    def __init__(self, consumer):
        self._consumer = consumer

    async def disconnect(self):
        g_id = self._consumer.get_game_id()
        game = await get_game(g_id)
        if not game.is_backuped:
            await self._send_game_end_info_to_opponent()
            add_delayed_task(
                f'limit_game_data_lifetime_{g_id}',
                settings.DELETE_GAME_TIMEOUT,
                settings.DELETE_GAME_TIMEOUT_FUNC
            )
            await game.backup()
            self.remove_all_delayed_tasks()
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
        
    def remove_all_delayed_tasks(self, game):
        teacher_id = game.teacher_player.id
        student_id = game.student_player.id
        remove_delayed_task(f'limit_action_time_{teacher_id}')
        remove_delayed_task(f'limit_action_time_{student_id}')
        remove_delayed_task(f'limit_reaction_time_{teacher_id}')
        remove_delayed_task(f'limit_reaction_time_{student_id}')
        remove_delayed_task(f'limit_hub_time_{teacher_id}')
        remove_delayed_task(f'limit_hub_time_{student_id}')
