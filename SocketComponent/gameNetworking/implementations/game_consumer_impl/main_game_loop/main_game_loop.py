from gameNetworking.enums import GameStage
from .hub_stage import HubStageHandler
from .clash_stage import ClashStageHandler
from .checkers import GameVerifier


# Main game loop function responsible for taking care of user requests to socket
class GameLoopHandler:
        
    def __init__(self, consumer, data):
        self._consumer = consumer
        self._data = data

    async def perform_game_loop(self):
        if not self._consumer.get_valid_json_sent(): return

        g_v = GameVerifier(self._consumer)
        if not await g_v.verify_game_exist(): return

        await self._consumer.refresh_game_user()
        await self._consumer.refresh_game()
        await self._consumer.refresh_opponent()
        message_type = self._data.get('type')
        g_stage = self._consumer.get_game_stage()
        if g_stage == GameStage.HUB:
            h_s_h = HubStageHandler(self._consumer, message_type, self._data)
            await h_s_h.perform_stage()
        else:
            c_s_h = ClashStageHandler(self._consumer, message_type, self._data)
            await c_s_h.perform_stage()
