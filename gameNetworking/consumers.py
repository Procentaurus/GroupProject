from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.conf import settings

from .implementations.game_consumer_impl.methods import *
from .implementations.game_consumer_impl.message_handling import *

class GameConsumer(AsyncJsonWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = None

        self._game = None
        self._winner = None
        self._game_user = None
        self._opponent = None

        self._is_closed_after_game_end = False
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

    ################################# Getters ##################################
    def get_game(self):
        return self._game

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
    
    def get_action_card_id_played_by_opp(self):
        return self._action_card_id_played_by_opp

    def get_game_stage(self):
        return self._game_stage

    def is_closed_after_game_end(self):
        return self._is_closed_after_game_end
    
    def get_action_moves_left(self):
        return self._moves_table[0]

    def get_reaction_moves_left(self):
        return self._moves_table[1]
    
    def is_winner(self):
        return (self._winner is not None)
    
    def is_time_for_moves_per_clash_inc(self):
        return self._turns_to_inc == 0
    
    def is_moves_per_clash_maximal(self):
        return self._moves_per_clash == (settings.MAX_MOVES_PER_CLASH - 1)

    ################################# Setters ##################################
    def close_after_game_end(self):
        self._is_closed_after_game_end = True

    def set_game(self, game):
        self._game = game

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

    ########################### Params updating methods ########################
    def reset_turns_to_inc(self):
        pass

    def decrement_turn_to_inc(self):
        pass

    def is_time_for_moves_per_clash_inc(self):
        pass

    def increment_moves_per_clash(self):
        pass

    def is_moves_per_clash_maximal(self):
        pass

    def limit_players_hub_time(self):
        pass

    def limit_player_action_time(self, player):
        pass

    def limit_player_reaction_time(self):
        pass

    def update_after_reconnect(self, game, player, opponent):
        pass

    def _update_moves_per_clash(self):
        pass

    def init_table_for_new_clash(self):
        pass

    def update_game_stage(self):
        pass

    async def refresh_game_user(self):
        pass

    async def refresh_game(self):
        pass

    async def refresh_opponent(self):
        pass

    def decrease_action_moves(self):
        pass

    def decrease_reaction_moves(self):
        pass

    def activate_logger(self):
        pass

    ############################ Basic consumer methods ########################
    async def connect(self):
        pass

    async def disconnect(self, *args):
        pass

    async def receive_json(self, data):
        pass

    async def decode_json(self, text_data, **kwargs):
        pass

    # sends messages to both players' mailboxes
    async def send_message_to_group(self, data, event):
        pass

    async def send_message_to_opponent(self, data, event):
        pass

    ############################ Message handlers ##############################
    async def opponent_move(self, data):
        pass

    async def opponent_disconnect(self, data=None):
        pass

    async def purchase_result(self, data):
        pass

    async def clash_result(self, data):
        pass

    async def card_package(self, data):
        pass

    async def game_start(self, data):
        pass

    async def clash_start(self, data):
        pass

    async def clash_end(self, data=None):
        pass

    async def game_reconnect(self, data):
        pass

    async def time_info(self, data):
        pass

    async def opponent_rejoin_waiting(self, data=None):
        pass

    async def game_end(self, data):
        pass

    async def game_creation(self, data):
        pass

    async def hub_stage_timeout(self, data=None):
        pass

    async def action_move_timeout(self, data=None):
        pass

    async def reaction_move_timeout(self, data=None):
        pass

    # Used for player's mistakes during game flow
    # that do not require complex response
    # Performs: logging and sending info to player
    async def error(self, message, log_message=None):
        pass

    # Used for player's mistakes during game flow
    # that do require complex response
    # Performs: logging and sending info to player
    async def complex_error(self, message, log_message, data):
        pass

    # Used for game flow errors
    # Performs: logging, sending info to player and closing connection
    async def critical_error(self, log_message):
        pass


GameConsumer.update_after_reconnect = update_after_reconnect
GameConsumer.reset_turns_to_inc = reset_turns_to_inc
GameConsumer.decrement_turn_to_inc = decrement_turn_to_inc
GameConsumer.increment_moves_per_clash = increment_moves_per_clash
GameConsumer.limit_players_hub_time = limit_players_hub_time
GameConsumer.limit_player_reaction_time = limit_player_reaction_time
GameConsumer.limit_player_action_time = limit_player_action_time
GameConsumer.update_game_stage = update_game_stage
GameConsumer._update_moves_per_clash = update_moves_per_clash
GameConsumer.decrease_action_moves = decrease_action_moves
GameConsumer.decrease_reaction_moves = decrease_reaction_moves
GameConsumer.refresh_game_user = refresh_game_user
GameConsumer.refresh_game = refresh_game
GameConsumer.refresh_opponent = refresh_opponent
GameConsumer.init_table_for_new_clash = init_table_for_new_clash
GameConsumer.activate_logger = activate_logger

GameConsumer.send_message_to_group = send_message_to_group
GameConsumer.send_message_to_opponent = send_message_to_opponent
GameConsumer.connect = connect
GameConsumer.disconnect = disconnect
GameConsumer.receive_json = receive_json
GameConsumer.decode_json = decode_json

GameConsumer.critical_error = critical_error
GameConsumer.complex_error = complex_error
GameConsumer.error = error
GameConsumer.reaction_move_timeout = reaction_move_timeout
GameConsumer.action_move_timeout = action_move_timeout
GameConsumer.hub_stage_timeout = hub_stage_timeout
GameConsumer.game_creation = game_creation
GameConsumer.game_end = game_end
GameConsumer.opponent_rejoin_waiting = opponent_rejoin_waiting
GameConsumer.time_info = time_info
GameConsumer.clash_end = clash_end
GameConsumer.game_reconnect = game_reconnect
GameConsumer.clash_start = clash_start
GameConsumer.game_start = game_start
GameConsumer.card_package = card_package
GameConsumer.clash_result = clash_result
GameConsumer.purchase_result =purchase_result
GameConsumer.opponent_disconnect = opponent_disconnect
GameConsumer.opponent_move = opponent_move
