import json

from gameNetworking.enums import GameStage
from gameNetworking.models.queries import get_game_user


def init_table_for_new_clash_impl(consumer):
    consumer._turns_to_inc -= 1
    if consumer._turns_to_inc == 0:
        consumer._turns_to_inc = consumer._turns_between_inc
        if consumer._action_moves_per_clash < consumer._max_moves_per_clash:
            consumer._action_moves_per_clash += 1

    for i in range(2):
        consumer._moves_table[i] = consumer._action_moves_per_clash

def update_game_stage_impl(consumer):
    if consumer.get_game_stage() == GameStage.HUB:
        consumer.set_game_stage(GameStage.CLASH)
    else:
        consumer.set_game_stage(GameStage.HUB)

async def refresh_game_user_impl(consumer):
    game_user_id = consumer.get_game_user().id
    refreshed_game_user = await get_game_user(game_user_id)
    consumer.set_game_user(refreshed_game_user)

async def decode_json_impl(consumer, text_data):
    try:
        json_data = json.loads(text_data)
        consumer.set_valid_json_sent(True)
        return json_data
    except json.JSONDecodeError:
        await consumer.error("Wrong format of sent json")
