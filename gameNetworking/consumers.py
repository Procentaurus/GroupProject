from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.exceptions import StopConsumer
import logging

from .implementations.game_consumer_impl.connect import connect_impl
from .implementations.game_consumer_impl.message_handling import *
from .implementations.game_consumer_impl.message_sending import *
from .implementations.game_consumer_impl.receive_json import main_game_loop_impl
from .implementations.game_consumer_impl.clean import *
from .implementations.game_consumer_impl.internal import *

class GameConsumer(AsyncJsonWebsocketConsumer):

    def __init__(self, *args, **kwargs): # intialization of variables used only by the current user
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)

        # game creation
        self.__game_id = None
        self.__game_user_id = None
        self.__opponent_channel_name = None

        # game closure
        self.__closure_from_user_side = True

        # game run
        self.__game_stage = GameStage.HUB
        self.__last_move_send_time = None
        self.__action_multiplier = 1 # specifies how many action moves can be done in 1 clash 
        self.__turns_after_action_multiplier_is_incremented = 5
        self.__moves_table = [1, 1] # this table represents number of moves that player performs in each clash
                                    # first number represent number of actions and the second number of reactions

    async def connect(self):
        await connect_impl(self)

    # standard cleanup procedure that should be triggered after self.close()
    async def cleanup(self):
        await cleanup_impl(self)

    # is called after game's end, when the end was triggered by the opponent or from standard cleanup procedure
    async def perform_cleanup(self):
        await perform_cleanup_impl(self)

    # is called when the user disconnests from socket
    async def disconnect(self, *args):
        await disconnect_impl(self)            
        raise StopConsumer()

    # responsible for managing current user messages, effectively main game loop function
    async def receive_json(self, data):
        await main_game_loop_impl(self, data)

    # sends messages to both players' mailboxes
    async def send_message_to_group(self, data, event):
        await send_message_to_group_impl(self, data, event)

    async def send_message_to_opponent(self, data, event):
        await send_message_to_opponent_impl(self, data, event)

    async def opponent_move(self, data):
        await opponent_move_impl(self, data)

    async def purchase_result(self, data):
        await purchase_result_impl(self, data)

    async def clash_result(self, data):
        await clash_result_impl(self, data)

    async def card_action(self, data):
        await card_action_impl(self, data)

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

    # Used for player's mistakes during game flow
    # that do not require complex response
    # Performs: logging and sending info to player
    async def perform_error_handling(self, message, log_message = None):
        await perform_error_handling_impl(self, message, log_message)

    # Used for player's mistakes during game flow
    # that do require complex response
    # Performs: logging and sending info to player
    async def perform_complex_error_handling(self, data,  message, log_message = None):
        await perform_complex_error_handling_impl(self, data, message, log_message)

    # Used for game flow errors
    # Performs: logging, sending info to player and closing connection
    async def perform_critical_error_handling(self, log_message):
        await perform_critical_error_handling_impl(self, log_message)

    def get_game_id(self):
        return self.__game_id

    def get_game_user_id(self):
        return self.__game_user_id
    
    def get_game_stage(self):
        return self.__game_stage

    def get_opponent_channel_name(self):
        return self.__opponent_channel_name

    def get_closure_from_user_side(self):
        return self.__closure_from_user_side

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
    
    def init_table_for_new_clash(self):
        init_table_for_new_clash_impl(self)

    def update_action_multiplier(self):
        update_action_multiplier_impl(self)

    def update_game_stage(self):
        update_game_stage_impl(self)
