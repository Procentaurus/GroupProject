from autobahn.exception import Disconnected

from gameMechanics.enums import PlayerState

from gameNetworking.queries import get_game_user

#
# Functions that manage messages from opponents and group,
# each function handles one message type that is the function's name
#

async def opponent_move_impl(consumer, data):
    if data.get("action_card") is not None:
        consumer.__action_card_played_by_opponent = data.get("action_card")
        await consumer.send_json({
            'type' : "opponent_move",
            'action_card' : data['action_card'],
        })
    elif data.get("reaction_cards") is not None:
        await consumer.send_json({
            'type' : "opponent_move",
            'reaction_cards' : data["reaction_cards"],
        })
    else:
        consumer.logger.debug("Wrong type of move.")


async def purchase_result_impl(consumer, data):
    await consumer.send_json({
        "type" : "purchase_result",
        "new_money_amount" : data["new_money_amount"]
    })

async def clash_result_impl(consumer, data):
    await consumer.send_json({
        'type': "clash_result",
        **data
    })

async def card_package_impl(consumer, data):
    cards = data['card']
    await consumer.send_json({
        'type' : "card_package",
        'cards' : cards,
    })

async def game_start_impl(consumer):
    await consumer.send_json({
        'type' : "game_start",
    })

async def clash_start_impl(consumer, data):
    game_user = await get_game_user(consumer.get_game_user_id())
    await game_user.set_current_state(PlayerState.IN_CLASH)
    consumer.update_game_stage()

    await consumer.send_json({
        'type' : "clash_start",
        'next_move' : data.get("next_move_player"),
    })

async def clash_end_impl(consumer):
    game_user = await get_game_user(consumer.get_game_user_id())
    await game_user.set_state(PlayerState.IN_HUB)
    consumer.update_game_stage()

    await consumer.send_json({
        'type' : "clash_end",
    })

async def game_end_impl(consumer, data):
    try:
        await consumer.send_json({
            'type' : "game_end",
            'winner' : data.get("winner"),
        })
    except Disconnected:
        consumer.logger.warning("Tried to sent through closed socket.")
        
    await consumer.close()

async def game_creation_impl(consumer, data):
    consumer.set_game_id(data["game_id"])
    consumer.set_opponent_channel_name(data["channel_name"])

async def error_impl(consumer, message, log_message):    
    await consumer.send_json({
        'type' : "error",
        'info' : message,
    })
    
    if log_message is None:
        consumer.logger.warning(message)
    else:
        consumer.logger.warning(log_message)

async def complex_error_impl(consumer, data, message, log_message):
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
    consumer.close()
