import json
from django.conf import settings

from ...enums import GameStage
from ...models.queries import get_game_user
from ...scheduler.scheduler import add_delayed_task


def init_table_for_new_clash_impl(consumer):
    consumer._turns_to_inc -= 1
    if consumer._turns_to_inc == 0:
        consumer._turns_to_inc = consumer._turns_between_inc
        if consumer._moves_per_clash < consumer._max_moves_per_clash:
            consumer._moves_per_clash += 1

    for i in range(2):
        consumer._moves_table[i] = consumer._moves_per_clash

def update_game_stage_impl(consumer):
    if consumer.get_game_stage() == GameStage.HUB:
        consumer.set_game_stage(GameStage.CLASH)
    else:
        consumer.set_game_stage(GameStage.HUB)

def limit_player_action_time_impl(consumer):
    add_delayed_task(
        f'limit_action_time_{consumer.get_opponent().id}',
        settings.ACTION_MOVE_TIMEOUT,
        settings.ACTION_MOVE_TIMEOUT_FUNC
    )

def limit_player_reaction_time_impl(consumer):
    add_delayed_task(
        f'limit_reaction_time_{consumer.get_opponent().id}',
        settings.REACTION_MOVE_TIMEOUT,
        settings.REACTION_MOVE_TIMEOUT_FUNC
    )

def limit_players_hub_time_impl(consumer):
    add_delayed_task(
        f'limit_hub_time_{consumer.get_game_user().id}',
        settings.HUB_STAGE_TIMEOUT,
        settings.HUB_STAGE_TIMEOUT_FUNC
    )
    add_delayed_task(
        f'limit_hub_time_{consumer.get_opponent().id}',
        settings.HUB_STAGE_TIMEOUT,
        settings.HUB_STAGE_TIMEOUT_FUNC
    )

async def refresh_game_user_impl(consumer):
    game_user_id = consumer.get_game_user().id
    refreshed_game_user = await get_game_user(game_user_id)
    consumer.set_game_user(refreshed_game_user)

async def refresh_opponent_impl(consumer):
    opp_id = consumer.get_opponent().id
    refreshed_opp = await get_game_user(opp_id)
    consumer.set_opponent(refreshed_opp)

async def decode_json_impl(consumer, text_data):
    try:
        json_data = json.loads(text_data)
        consumer.set_valid_json_sent(True)
        return json_data
    except json.JSONDecodeError:
        await consumer.error("Wrong format of sent json")
