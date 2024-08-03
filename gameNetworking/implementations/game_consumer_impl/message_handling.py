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

async def opponent_move_impl(consumer, data):
    if data.get("action_card") is not None:
        a_card = data.get("action_card")
        consumer.set_action_card_id_played_by_opp(a_card["id"])
        await consumer.send_json({
            'type' : "opponent_move",
            'action_card' : a_card,
        })
    else:
        await consumer.send_json({
            'type' : "opponent_move",
            'reaction_cards' : data.get("reaction_cards"),
        })

async def opponent_disconnect_impl(consumer):
    await consumer.send_json({
        "type" : "opponent_disconnect"
    })
    await consumer.close()

async def purchase_result_impl(consumer, data):
    await consumer.send_json({
        "type" : "purchase_result",
        "new_money_amount" : data.get("new_money_amount")
    })

async def clash_result_impl(consumer, data):
    await consumer.send_json({
        'type': "clash_result",
        **data
    })

async def card_package_impl(consumer, data):
    await consumer.send_json({
        'type' : "card_package",
        **data
    })

async def game_start_impl(consumer, data):
    await consumer.send_json({
        'type' : "game_start",
        **data
    })

async def clash_start_impl(consumer, data):
    game_user = consumer.get_game_user()
    game_id = str(consumer.get_game().id)
    update_game_user_state(str(game_id), str(game_user.id), PlayerState.IN_CLASH)
    consumer.update_game_stage()
    await consumer.send_json({
        'type' : "clash_start",
        'next_move' : data.get("next_move_player"),
    })

async def clash_end_impl(consumer):
    consumer.init_table_for_new_clash()
    consumer.update_game_stage()
    await consumer.send_json({
        'type' : "clash_end",
    })

async def game_reconnect_impl(consumer, data):
    await consumer.refresh_opponent()
    await consumer.send_json({
        'type' : "game_reconnect",
        **data
    })

async def time_info_impl(consumer, data):
    await consumer.send_json({
        "type": "time_info",
        "time_remaining": data.get("time_remaining")
    })

async def opponent_rejoin_waiting_impl(consumer):
    await consumer.send_json({
        'type' : "opponent_rejoin_waiting",
        'time_for_opponent_to_rejoin' : settings.REJOIN_TIMEOUT
    })

async def game_end_impl(consumer, data):  
    try:
        await consumer.send_json({
            'type' : "game_end",
            **data
        })
        if data.get('after_surrender') == True:
            consumer.set_closed_after_disconnect(False)
            consumer.set_winner(data.get('winner'))
    except Disconnected:
        consumer.logger.warning("Tried to sent through closed socket.")

    await consumer.close()

async def game_creation_impl(consumer, data):
    game = await get_game(data.get("game_id"))
    consumer.set_game(game)
    opponent = await get_game_user(data.get("opponent_id"))
    consumer.set_opponent(opponent)

async def hub_stage_timeout_impl(consumer):
    consumer.logger.info("Hub stage timeout")
    await consumer.send_json({
        'type': "timeout",
        'move': 'ready move'
    })
    handler = ReadyMoveHandler(consumer)
    await handler.perform_move(True)

async def action_move_timeout_impl(consumer):
    consumer.logger.info("Action move timeout")
    await consumer.send_json({
        'type': "timeout",
        'move': 'action move'
    })

async def reaction_move_timeout_impl(consumer):
    consumer.logger.info("Reaction move timeout")
    await consumer.send_json({
        'type': "timeout",
        'move': 'reaction move'
    })
    handler = ReactionMoveHandler(
        consumer,
        {'reaction_cards': []}
    )
    await handler.perform_move(True)

async def error_impl(consumer, message, log_message):    
    await consumer.send_json({
        'type' : "error",
        'info' : message,
    })

    if log_message is None:
        consumer.logger.warning(message)
    else:
        consumer.logger.warning(log_message)

async def complex_error_impl(consumer, message, log_message, data):
    await consumer.send_json({
        'type' : "error",
        'info' : message,
        **data,
    })

    if log_message is None:
        consumer.logger.warning(message)
    else:
        consumer.logger.warning(log_message)

async def critical_error_impl(consumer, log_message):
    await consumer.send_json({
        'type' : "error",
        'info' : "SERVER ERROR OCCURED",
    })
    consumer.logger.error(log_message)
