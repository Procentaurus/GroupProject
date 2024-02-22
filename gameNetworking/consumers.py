from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.exceptions import StopConsumer
import logging

from .implementations.game_consumer_impl.clean import disconnect_impl
from .implementations.game_consumer_impl.sync_methods import *
from .implementations.game_consumer_impl.connect import connect_impl
from .implementations.game_consumer_impl.message_handling import *
from .implementations.game_consumer_impl.message_sending import *
from .implementations.game_consumer_impl.main_game_loop.main_game_loop_impl \
    import main_game_loop_impl


class GameConsumer(AsyncJsonWebsocketConsumer):

    # intialization of variables used only by the current user
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)

        self.__game_id = None
        self.__winner = None
        self.__game_user_id = None
        self.__opponent_channel_name = None
        self.__closure_from_user_side = True

        self.__game_stage = GameStage.HUB
        self.__action_card_played_by_opponent = None
        self.__last_move_send_time = None

        # Specifies how many action moves can be done in 1 clash 
        self.__moves_per_clash = 1
        self.__max_moves_per_clash = 3

        # Number of turns that specify how often action_moves_per_clash
        # is incremented
        self.__turns_between_incrementations = (5 - 1)

        #Number of turns until the next incrementation
        self.__turns_to_incrementation = (5 - 1)

        # This table represents number of moves that
        # player performs in each clash.
        # Index 0 represent number of actions
        # and index 1 number of reactions
        self.__moves_table = [1, 1]

    async def connect(self):
        await connect_impl(self)

    # is called when socket connection is close
    async def disconnect(self, *args):
        await disconnect_impl(self)            
        raise StopConsumer()

    # responsible for managing current user messages,
    # effectively main game loop function
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

    async def card_package(self, data):
        await card_package_impl(self, data)

    async def game_start(self, data):
        await game_start_impl(self, data)

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
    async def error(self, message, log_message = None):
        await error_impl(self, message, log_message)

    # Used for player's mistakes during game flow
    # that do require complex response
    # Performs: logging and sending info to player
    async def complex_error(self, message, log_message = None, **data):
        await complex_error_impl(self, message, log_message, data)

    # Used for game flow errors
    # Performs: logging, sending info to player and closing connection
    async def critical_error(self, log_message):
        await critical_error_impl(self, log_message)

    def get_game_id(self):
        return self.__game_id

    def get_game_user_id(self):
        return self.__game_user_id

    def get_winner(self):
        return self.__winner
    
    def get_action_card_played_by_opponent(self):
        return self.__action_card_played_by_opponent
    
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
    
    def set_closure_from_user_side(self, closure_from_user_side):
        self.__closure_from_user_side = closure_from_user_side
    
    def set_game_id(self, game_id):
        self.__game_id = game_id

    def set_winner(self, winner):
        self.__winner = winner

    def set_action_card_played_by_opponent(self, action_card_id):
        self.__action_card_played_by_opponent = action_card_id
    
    def set_game_user_id(self, game_user_id):
        self.__game_user_id = game_user_id

    def set_opponent_channel_name(self, opponent_channel_name):
        self.__opponent_channel_name = opponent_channel_name
    
    def init_table_for_new_clash(self):
        init_table_for_new_clash_impl(self)

    def update_game_stage(self):
        update_game_stage_impl(self)
