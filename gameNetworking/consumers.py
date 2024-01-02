from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.exceptions import StopConsumer
import logging

from .mechanics.game_consumer_impl.connect import connect_impl
from .mechanics.game_consumer_impl.message_handlers import *
from .mechanics.game_consumer_impl.message_senders import *
from .mechanics.game_consumer_impl.receive_json import main_game_loop_impl
from .mechanics.game_consumer_impl.cleaners import *

class GameConsumer(AsyncJsonWebsocketConsumer):

    def __init__(self, *args, **kwargs): # intialization of variables used only by the current user
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)

        # game creation
        self.game_id = None
        self.game_user_id = None
        self.opponent_channel_name = None

        # game closure
        self.winner = None
        self.closure_from_user_side = True

        # game run
        self.number_of_game_iterations = 1
        self.moves_table = [[2,[2,2],1,[1,1]]*self.number_of_game_iterations]

        self.last_move_send_time = None

    async def connect(self):
        await connect_impl(self)

    async def cleanup(self): # standard cleanup procedure that should be triggered after self.close()
        await cleanup_impl(self)

    async def perform_cleanup(self): # is called after game's end, when the end was triggered by the opponent or from standard cleanup procedure
        await perform_cleanup_impl(self)

    async def disconnect(self, *args):
        await disconnect_impl(self)            
        raise StopConsumer()

    async def receive_json(self, data): # responsible for managing current user messages, effectively main game loop function
        await main_game_loop_impl(self, data)

    async def send_message_to_group(self, data, event): # sends messages to both players' clients
        await send_message_to_group_impl(self, data, event)

    async def send_message_to_opponent(self, data, event):
        await send_message_to_opponent_impl(self, data, event)

    async def opponent_move(self, data):
        await opponent_move_impl(self, data)

    async def clash_result(self, data):
        await clash_result_impl(self, data)

    async def collect_action(self, data):
        await collect_action_impl(self,data)

    async def game_start(self, data):
        await game_start_impl(self, data)

    async def game_end(self, data):
        await game_end_impl(self, data)

    async def game_creation(self, data):
        await game_creation_impl(self, data)

    async def error(self, info):
        await error_impl(self, info)
