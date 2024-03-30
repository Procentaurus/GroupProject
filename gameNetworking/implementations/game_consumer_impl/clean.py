from gameNetworking.models.queries import *

class Disconnector:

    def __init__(self, consumer):
        self._consumer = consumer

    async def disconnect(self):
        g_id = self._consumer.get_game_id()
        game = await get_game(g_id)
        if game is not None:
            await self._clean_game(game)
            await self._send_game_end_info_to_opponent()

        await self._clean_game_user()
        await self._remove_player_from_group(g_id)

    async def _send_cleanup_error(self, obj):
        await self._consumer.error(
            f"Couldnt clean up {obj} instance after the game")
        
    async def _send_game_end_info_to_opponent(self):
        w = self._consumer.get_winner()
        if not self._consumer.get_closure_from_user_side():
            await self._consumer.send_message_to_opponent(
                {"winner" : w}, "game_end")
        else:
            await self._consumer.send_message_to_opponent(
                {"winner" : w, "after_disconnect" : True}, "game_end")

    async def _clean_game_user(self):
        game_user = self._consumer.get_game_user()
        if game_user:
            succesful_delete = await delete_game_user(game_user.id)
            if not succesful_delete:
                await self._send_cleanup_error("game_user")

    async def _clean_game(self, game):
        succesful_delete = await delete_game(game.id)
        if not succesful_delete:
            await self._send_cleanup_error("game")

    async def _remove_player_from_group(self, game_id):
        await self._consumer.channel_layer.group_discard(
            f"game_{game_id}", self._consumer.channel_name)
