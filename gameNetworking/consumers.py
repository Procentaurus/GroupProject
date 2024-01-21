from typing import Any
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
        self.__game_id = None
        self.__game_user_id = None
        self.__opponent_channel_name = None

        # game closure
        self.__winner = None
        self.__closure_from_user_side = True

        # game run
        self.__last_move_send_time = None
        self.__number_of_game_iterations = 1
        self.__moves_table = [[2, [2,2], 1, [1,1]] * self.get_number_of_game_iterations()] # this table represents number of moves that player can perform in each game stage
        # elems of indexes 0 and 2 are number of moves in first collecting phase and second collecting phase
        # elems of indexes 1 and 3 are sets that represent number of moves in first and second clash stage,
        # in each set the elem of index 0 is the number of action moves and the one of index 1 is the number of reaction moves

    async def connect(self):
        await connect_impl(self)

    async def cleanup(self): # standard cleanup procedure that should be triggered after self.close()
        await cleanup_impl(self)

    async def perform_cleanup(self): # is called after game's end, when the end was triggered by the opponent or from standard cleanup procedure
        await perform_cleanup_impl(self)

    async def disconnect(self, *args): # is called when the user disconnests from socket
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

    async def card_action(self, data):
        await card_action_impl(self,data)

    async def task_action(self, data):
        await task_action_impl(self,data)

    async def game_start(self, data = None):
        await game_start_impl(self)

    async def clash_start(self, data):
        await clash_start_impl(self, data)

    async def clash_end(self, data = None):
        await clash_end_impl(self)

    async def game_end(self, data):
        await game_end_impl(self, data)

    async def game_creation(self, data):
        await game_creation_impl(self, data)

    async def error(self, info):
        await error_impl(self, info)

    def get_game_id(self):
        return self.__game_id

    def get_game_user_id(self):
        return self.__game_user_id

    def get_opponent_channel_name(self):
        return self.__opponent_channel_name

    def get_winner(self):
        return self.__winner

    def get_closure_from_user_side(self):
        return self.__closure_from_user_side

    def get_number_of_game_iterations(self):
        return self.__number_of_game_iterations

    def get_moves_table(self):
        return self.__moves_table

    def get_last_move_send_time(self):
        return self.__last_move_send_time
    
    def set_game_id(self, game_id):
        self.__game_id = game_id
    
    def set_game_user_id(self, game_user_id):
        self.__game_user_id = game_user_id

    def set_opponent_channel_name(self, opponent_channel_name):
        self.__opponent_channel_name = opponent_channel_name

    def set_winner(self, winner):
        self.__winner = winner