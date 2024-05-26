from autobahn.exception import Disconnected

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
        consumer.set_a_card_played_by_opponent(a_card["id"])
        await consumer.send_json({
            'type' : "opponent_move",
            'action_card' : a_card,
        })
    else:
        await consumer.send_json({
            'type' : "opponent_move",
            'reaction_cards' : data.get("reaction_cards"),
        })

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
    await game_user.set_state("in_clash")
    consumer.update_game_stage()

    await consumer.send_json({
        'type' : "clash_start",
        'next_move' : data.get("next_move_player"),
    })

async def clash_end_impl(consumer):
    consumer.update_game_stage()
    await consumer.send_json({
        'type' : "clash_end",
    })

async def game_end_impl(consumer, data):  
    try:
        await consumer.send_json({
            'type' : "game_end",
            **data
        })
    except Disconnected:
        consumer.logger.warning("Tried to sent through closed socket.")

    await consumer.close()

async def game_creation_impl(consumer, data):
    consumer.set_game_id(data.get("game_id"))
    consumer.set_opponent_channel_name(data.get("channel_name"))

    opp = await get_game_user(data.get("opponent_id"))
    consumer.set_opponent(opp)

async def hub_stage_timeout_impl(consumer):
    consumer.logger.info("Hub stage timeout")
    game = await get_game(consumer.get_game_id())
    handler = ReadyMoveHandler(consumer, game)
    await handler.perform_move(True)

async def action_move_timeout_impl(consumer):
    consumer.logger.info("Action move timeout")

async def reaction_move_timeout_impl(consumer):
    consumer.logger.info("Reaction move timeout")
    game = await get_game(consumer.get_game_id())
    handler = ReactionMoveHandler(
        consumer,
        game,
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
