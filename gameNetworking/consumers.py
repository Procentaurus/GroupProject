from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.exceptions import StopConsumer
import logging
from django.conf import settings

from .implementations.game_consumer_impl.disconnect import Disconnector
from .implementations.game_consumer_impl.methods import *
from .implementations.game_consumer_impl.connect import Connector
from .implementations.game_consumer_impl.message_handling import *
from .implementations.game_consumer_impl.message_sending import *
from .implementations.game_consumer_impl.main_game_loop.main_game_loop \
    import GameLoopHandler


class GameConsumer(AsyncJsonWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)

        self._game_id = None
        self._winner = None
        self._game_user = None
        self._opponent = None

        self._closed_after_disconnect = True
        self._valid_json_sent = False

        self._game_stage = GameStage.HUB
        self._action_card_id_played_by_opp = None
        self._moves_per_clash = settings.INIT_MOVES_PER_CLASH

        # Number of turns until the next incrementation
        self._turns_to_inc = (settings.TURNS_BETWEEN_NUM_MOVES_INC - 1)

        # This table represents number of moves that
        # player performs in each clash.
        # Index 0 represent number of actions
        # and index 1 number of reactions
        self._moves_table = [
            settings.INIT_MOVES_PER_CLASH,
            settings.INIT_MOVES_PER_CLASH
        ]

    ##### Getters #####
    def get_game_id(self):
        return self._game_id
    
    def get_turns_to_inc(self):
        return self._turns_to_inc
    
    def get_moves_per_clash(self):
        return self._moves_per_clash
    
    def get_opponent(self):
        return self._opponent

    def get_valid_json_sent(self):
        return self._valid_json_sent

    def get_game_user(self):
        return self._game_user
    
    def get_winner(self):
        return self._winner
    
    ##### Setters #####
    def set_closed_after_disconnect(self, closed_after_disconnect):
        self._closed_after_disconnect = closed_after_disconnect
    
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

    def set_action_card_id_played_by_opp(self, action_card_id):
        self._action_card_id_played_by_opp = action_card_id
    
    def set_game_user(self, game_user):
        self._game_user = game_user

    ##### State changing functions #####
    def is_winner(self):
        return (self._winner is not None)
    
    def reset_turns_to_inc(self):
        self._turns_to_inc = (settings.TURNS_BETWEEN_NUM_MOVES_INC - 1)
    
    def decrement_turn_to_inc(self):
        self._turns_to_inc -= 1

    def is_time_for_moves_per_clash_incrementation(self):
        return self._turns_to_inc == 0

    def increment_moves_per_clash(self):
        self._moves_per_clash += 1

    def is_moves_per_clash_maximal(self):
        return self._moves_per_clash == (settings.MAX_MOVES_PER_CLASH - 1)

    def get_action_card_id_played_by_opp(self):
        return self._action_card_id_played_by_opp

    def get_game_stage(self):
        return self._game_stage

    def closed_after_disconnect(self):
        return self._closed_after_disconnect

    def limit_players_hub_time(self):
        limit_players_hub_time_impl(self)

    def limit_player_action_time(self, player_side):
        limit_player_action_time_impl(self, player_side)

    def limit_player_reaction_time(self):
        limit_player_reaction_time_impl(self)

    def update_after_reconnect(self, game, player, opponent):
        pass

    def _update_moves_per_clash(self):
        update_moves_per_clash_impl(self)

    def init_table_for_new_clash(self):
        self._update_moves_per_clash()
        for i in range(2):
            self._moves_table[i] = self._moves_per_clash

    def update_game_stage(self):
        update_game_stage_impl(self)

    async def refresh_game_user(self):
        await refresh_game_user_impl(self)

    async def refresh_opponent(self):
        await refresh_opponent_impl(self)
    
    def get_action_moves_left(self):
        return self._moves_table[0]

    def get_reaction_moves_left(self):
        return self._moves_table[1]
    
    def decrease_action_moves(self):
        self._moves_table[0] -= 1

    def decrease_reaction_moves(self):
        self._moves_table[1] -= 1

    ##### Basic consumer methods #####
    async def connect(self):
        connector = Connector(self)
        await connector.connect()

    async def disconnect(self, *args):
        disconnector = Disconnector(self)
        await disconnector.disconnect()           
        raise StopConsumer()

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

    ##### Message handlers #####
    async def opponent_move(self, data):
        await opponent_move_impl(self, data)

    async def opponent_disconnect(self, data=None):
        await opponent_disconnect_impl(self)

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

    async def game_reconnect(self, data):
        await game_reconnect_impl(self, data)

    async def time_info(self, data):
        await time_info_impl(self, data)

    async def opponent_rejoin_waiting(self, data=None):
        await opponent_rejoin_waiting_impl(self)

    async def game_end(self, data):
        await game_end_impl(self, data)

    async def game_creation(self, data):
        await game_creation_impl(self, data)

    async def hub_stage_timeout(self, data=None):
        await hub_stage_timeout_impl(self)

    async def action_move_timeout(self, data=None):
        await action_move_timeout_impl(self)

    async def reaction_move_timeout(self, data=None):
        await reaction_move_timeout_impl(self)

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

GameConsumer.update_after_reconnect = update_after_reconnect_impl
