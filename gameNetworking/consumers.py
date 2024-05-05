from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.exceptions import StopConsumer
import logging

from .implementations.game_consumer_impl.clean import Disconnector
from .implementations.game_consumer_impl.methods import *
from .implementations.game_consumer_impl.connect import Connector
from .implementations.game_consumer_impl.message_handling import *
from .implementations.game_consumer_impl.message_sending import *
from .implementations.game_consumer_impl.main_game_loop.main_game_loop \
    import GameLoopHandler


class GameConsumer(AsyncJsonWebsocketConsumer):

    # intialization of variables used only by the current user
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)

        self._game_id = None
        self._winner = None
        self._game_user = None
        self._opponent = None
        self._opponent_channel_name = None

        self._closure_from_user_side = True
        self._valid_json_sent = False

        self._game_stage = GameStage.HUB
        self._a_card_played_by_opponent = None
        self._last_move_send_time = None

        # Specifies how many action moves can be done in 1 clash 
        self._moves_per_clash = 1
        self._max_moves_per_clash = 3

        # Number of turns that specify how often action_moves_per_clash
        # is incremented
        self._turns_between_inc = (5 - 1)

        #Number of turns until the next incrementation
        self._turns_to_inc = (5 - 1)

        # This table represents number of moves that
        # player performs in each clash.
        # Index 0 represent number of actions
        # and index 1 number of reactions
        self._moves_table = [1, 1]

    async def connect(self):
        connector = Connector(self)
        await connector.connect()

    # is called when socket connection is close
    async def disconnect(self, *args):
        disconnector = Disconnector(self)
        await disconnector.disconnect()           
        raise StopConsumer()

    # responsible for managing current user messages,
    # effectively main game loop function
    async def receive_json(self, data):
        loop_handler = GameLoopHandler(self, data)
        await loop_handler.perform_game_loop()
        self.set_valid_json_sent(False)

    async def decode_json(self, text_data, **kwargs):
        json_data = await decode_json_impl(self, text_data)
        return json_data

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

    async def clash_end(self, data=None):
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
    async def complex_error(self, message, log_message, data):
        await complex_error_impl(self, message, log_message, data)

    # Used for game flow errors
    # Performs: logging, sending info to player and closing connection
    async def critical_error(self, log_message):
        await critical_error_impl(self, log_message)
        await self.close()

    def get_game_id(self):
        return self._game_id
    
    def get_opponent(self):
        return self._opponent

    def get_valid_json_sent(self):
        return self._valid_json_sent

    def get_game_user(self):
        return self._game_user
    
    def get_winner(self):
        return self._winner

    def is_winner(self):
        return (self._winner is not None)
    
    def get_a_card_played_by_opponent(self):
        return self._a_card_played_by_opponent
    
    def get_game_stage(self):
        return self._game_stage

    def get_opponent_channel_name(self):
        return self._opponent_channel_name

    def get_closure_from_user_side(self):
        return self._closure_from_user_side

    def get_last_move_send_time(self):
        return self._last_move_send_time
    
    def set_closure_from_user_side(self, closure_from_user_side):
        self._closure_from_user_side = closure_from_user_side
    
    def set_game_id(self, game_id):
        self._game_id = game_id

    def set_opponent(self, opponent):
        self._opponent = opponent

    def set_valid_json_sent(self, val):
        self._valid_json_sent = val

    def set_winner(self, winner):
        self._winner = winner

    def set_game_stage(self, game_stage):
        self._game_stage = game_stage

    def set_a_card_played_by_opponent(self, action_card_id):
        self._a_card_played_by_opponent = action_card_id
    
    def set_game_user(self, game_user):
        self._game_user = game_user

    def set_opponent_channel_name(self, opponent_channel_name):
        self._opponent_channel_name = opponent_channel_name
    
    def init_table_for_new_clash(self):
        init_table_for_new_clash_impl(self)

    def update_game_stage(self):
        update_game_stage_impl(self)

    async def refresh_game_user(self):
        await refresh_game_user_impl(self)

    async def refresh_opponent(self):
        await refresh_opponent_impl(self)

    def no_action_moves_left(self):
        return self._moves_table[0] == 0

    def no_reaction_moves_left(self):
        return self._moves_table[1] == 0
    
    def decrease_action_moves(self):
        # 0 is index of action moves
        self._moves_table[0] -= 1

    def decrease_reaction_moves(self):
        # 1 is index of reaction moves
        self._moves_table[1] -= 1

