from autobahn.exception import Disconnected
from django.conf import settings

from ...scheduler.scheduler import update_game_user_state
from ...enums import PlayerState
from ...implementations.game_consumer_impl.main_game_loop.hub_stage import \
    ReadyMoveHandler
from ...implementations.game_consumer_impl.main_game_loop.clash_stage import \
    ReactionMoveHandler
from ...models.queries import get_game_user, get_game
from .main_game_loop.common import *


#
# Functions that manage messages from opponents and group,
# each function handles one message type that is the function's name
#

async def opponent_move(self, data):
    if data.get("action_card") is not None:
        a_card = data.get("action_card")
        self.set_action_card_id_played_by_opp(a_card["id"])
        await self.send_json({
            'type' : "opponent_move",
            'action_card' : a_card,
        })
    else:
        await self.send_json({
            'type' : "opponent_move",
            'reaction_cards' : data.get("reaction_cards"),
        })

async def opponent_disconnect(self, data=None):
    await self.send_json({
        "type" : "opponent_disconnect"
    })
    await self.close()

async def purchase_result(self, data):
    await self.send_json({
        "type" : "purchase_result",
        "new_money_amount" : data.get("new_money_amount")
    })

async def clash_result(self, data):
    await self.send_json({
        'type': "clash_result",
        **data
    })

async def card_package(self, data):
    await self.send_json({
        'type' : "card_package",
        **data
    })

async def game_start(self, data):
    await self.send_json({
        'type' : "game_start",
        **data
    })

async def clash_start(self, data):
    game_user = self.get_game_user()
    game_id = str(self.get_game().id)
    update_game_user_state(str(game_id), str(game_user.id), PlayerState.IN_CLASH)
    self.update_game_stage()
    await self.send_json({
        'type' : "clash_start",
        'next_move' : data.get("next_move_player"),
    })

async def clash_end(self, data=None):
    self.init_table_for_new_clash()
    self.update_game_stage()
    await self.send_json({
        'type' : "clash_end",
    })

async def game_reconnect(self, data):
    await self.refresh_opponent()
    await self.send_json({
        'type' : "game_reconnect",
        **data
    })

async def time_info(self, data):
    await self.send_json({
        "type": "time_info",
        "time_remaining": data.get("time_remaining")
    })

async def opponent_rejoin_waiting(self, data=None):
    await self.send_json({
        'type' : "opponent_rejoin_waiting",
        'time_for_opponent_to_rejoin' : settings.REJOIN_TIMEOUT
    })

async def game_end(self, data):  
    try:
        await self.send_json({
            'type' : "game_end",
            **data
        })
        self.set_closed_after_disconnect(False)
        self.set_winner(data.get('winner'))
    except Disconnected:
        self.logger.warning("Tried to sent through closed socket.")

    await self.close()

async def game_creation(self, data):
    game = await get_game(data.get("game_id"))
    self.set_game(game)
    opponent = await get_game_user(data.get("opponent_id"))
    self.set_opponent(opponent)

async def hub_stage_timeout(self, data=None):
    self.logger.info("Hub stage timeout")
    await self.send_json({
        'type': "timeout",
        'move': 'ready move'
    })
    await self.refresh_game_user()
    await self.refresh_game()
    handler = ReadyMoveHandler(self)
    await handler.perform_move(True)

async def action_move_timeout(self, data=None):
    self.logger.info("Action move timeout")
    await self.send_json({
        'type': "timeout",
        'move': 'action move'
    })
    await self.refresh_game_user()
    await self.refresh_game()

async def reaction_move_timeout(self, data=None):
    self.logger.info("Reaction move timeout")
    await self.send_json({
        'type': "timeout",
        'move': 'reaction move'
    })
    await self.refresh_game_user()
    await self.refresh_game()
    handler = ReactionMoveHandler(self, {'reaction_cards': []})
    await handler.perform_move(True)

async def error(self, message, log_message=None):    
    await self.send_json({
        'type' : "error",
        'info' : message,
    })
    if log_message is None:
        self.logger.warning(message)
    else:
        self.logger.warning(log_message)

async def complex_error(self, message, log_message, data):
    await self.send_json({
        'type' : "error",
        'info' : message,
        **data,
    })

    if log_message is None:
        self.logger.warning(message)
    else:
        self.logger.warning(log_message)

async def critical_error(self, log_message):
    await self.send_json({
        'type' : "error",
        'info' : "SERVER ERROR OCCURED",
    })
    self.logger.error(log_message)
    await self.close()
