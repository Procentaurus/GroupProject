from autobahn.exception import Disconnected

from gameMechanics.enums import PlayerState

from gameNetworking.queries import get_game_user

#
# Functions that manage messages from opponents and group,
# each function handles one message type that is the function's name
#

async def opponent_move_impl(consumer, data):
    data = data['data']

    if data.get("action_card") is not None:
        await consumer.send_json({
            'type': "opponent_move",
            'action_card':  data['action_card'],
        })
    elif data.get("reaction_cards") is not None:
        await consumer.send_json({
            'type': "opponent_move",
            'reaction_cards':  data["reaction_cards"],
        })
    else:
        consumer.logger.debug("Wrong type of move.")

async def clash_result_impl(consumer, data):
    data = data["data"]

    student_new_morale = data["student_new_morale"]
    teacher_new_morale = data["teacher_new_morale"]

    await consumer.send_json({
        'type': "clash_result",
        'student_new_morale': student_new_morale,
        'teacher_new_morale': teacher_new_morale,
    })

async def card_action_impl(consumer, data):
    data = data['data']

    cards = data['card']
    await consumer.send_json({
        'type': "collect_action",
        'cards': cards,
    })

async def game_start_impl(consumer):
    await consumer.send_json({
        'type': "game_start",
    })

async def clash_start_impl(consumer, data):
    data = data['data']

    game_user = await get_game_user(consumer.get_game_user_id())
    await game_user.set_current_state(PlayerState.IN_CLASH)
    consumer.update_game_stage()

    await consumer.send_json({
        'type': "clash_start",
        'next_move': data.get("next_move_player"),
    })

async def clash_end_impl(consumer):
    game_user = await get_game_user(consumer.get_game_user_id())
    await game_user.set_state(PlayerState.IN_HUB)
    consumer.update_game_stage()

    await consumer.send_json({
        'type': "clash_end",
    })

async def game_end_impl(consumer, data):
    data = data['data']

    try:
        await consumer.send_json({
            'type': "game_end",
            'winner': data.get("winner"),
        })
    except Disconnected:
        consumer.logger.warning("Tried to sent through closed socket.")
        
    await consumer.close()

async def game_creation_impl(consumer, data):
    data = data['data']
    
    consumer.set_game_id(data["game_id"])
    consumer.set_opponent_channel_name(data["channel_name"])

async def perform_error_handling_impl(consumer, message, log_message):    
    await consumer.send_json({
        'type': "error",
        'info': message,
    })
    
    if log_message is None:
        consumer.logger.warning(message)
    else:
        consumer.logger.warning(log_message)

async def perform_complex_error_handling_impl(consumer, data, message, log_message):
    data = data['data']

    await consumer.send_json({
        'type': "error",
        'info': message,
        **data,
    })

    if log_message is None:
        consumer.logger.warning(message)
    else:
        consumer.logger.warning(log_message)

async def perform_critical_error_handling_impl(consumer, log_message):
    await consumer.send_json({
        'type': "error",
        'info': "SERVER ERROR OCCURED",
    })

    consumer.logger.error(log_message)
