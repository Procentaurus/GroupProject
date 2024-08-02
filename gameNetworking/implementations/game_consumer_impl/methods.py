import json
from django.conf import settings

from ...enums import GameStage
from ...models.queries import get_game_user, get_game
from ...scheduler.scheduler import add_delayed_task

def update_after_reconnect_impl(self, game, player, opponent):
    self._opponent = opponent
    self._game_user = player
    self._game = game
    self._game_stage = GameStage.CLASH if game.stage else GameStage.HUB
    self._turns_to_inc = game.turns_to_inc
    self._moves_per_clash = game.moves_per_clash
    self._action_card_id_played_by_opp = player.opp_played_action_card_id
    self._moves_table = [
        player.action_moves_left,
        player.reaction_moves_left
    ]

def update_moves_per_clash_impl(consumer):
    consumer.decrement_turn_to_inc()
    if consumer.is_time_for_moves_per_clash_incrementation():
        consumer.reset_turns_to_inc()
        if not consumer.is_moves_per_clash_maximal():
            consumer.increment_moves_per_clash()

def update_game_stage_impl(consumer):
    if consumer.get_game_stage() == GameStage.HUB:
        consumer.set_game_stage(GameStage.CLASH)
    else:
        consumer.set_game_stage(GameStage.HUB)

def limit_player_action_time_impl(consumer, player_side):
    opp = consumer.get_opponent()
    g_u = consumer.get_game_user()
    id = opp.id if player_side == opp.conflict_side else g_u.id
    add_delayed_task(
        f'limit_action_time_{id}',
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
    print(f"limit_players_hub_time, player_id={consumer.get_game_user().id}")
    print(f"limit_players_hub_time, opp_id={consumer.get_opponent().id}")
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

async def refresh_game_impl(consumer):
    game_id = consumer.get_game().id
    refreshed_game = await get_game(game_id)
    consumer.set_game(refreshed_game)

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
