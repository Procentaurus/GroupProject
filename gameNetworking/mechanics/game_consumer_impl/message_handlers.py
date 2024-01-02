from autobahn.exception import Disconnected

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

async def collect_action_impl(consumer, data):
    data = data['data']
    task = data['task']
    await consumer.send_json({
        'type': "collect_action",
        'task': task,
    })

async def game_start_impl(consumer, data):
    game_data = data['data']

    await consumer.send_json({
        'type': "game_start",
        'next_move': game_data.get("next_move_player"),
        'start_datetime': game_data.get("start_datetime"),
    })

async def game_end_impl(consumer, data):
    winner = data['data']
    try:
        await consumer.send_json({
            'type': "game_end",
            'winner': winner,
        })
    except Disconnected:
        consumer.logger.warning("Tried to sent through closed socket.")
        
    await consumer.close()

async def game_creation_impl(consumer, data):
    data = data['data']
    consumer.game_id = data["game_id"]
    consumer.opponent_channel_name = data["channel_name"]

async def error_impl(consumer, info):
    await consumer.send_json({
        'type': "error",
        'info': info,
    })