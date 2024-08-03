import json
from django.conf import settings

from ...enums import GameStage
from ...models.queries import get_game_user, get_game
from ...scheduler.scheduler import add_delayed_task


def is_winner(self):
    return (self._winner is not None)

def reset_turns_to_inc(self):
    self._turns_to_inc = (settings.TURNS_BETWEEN_NUM_MOVES_INC - 1)

def decrement_turn_to_inc(self):
    self._turns_to_inc -= 1

def is_time_for_moves_per_clash_inc(self):
    return self._turns_to_inc == 0

def increment_moves_per_clash(self):
    self._moves_per_clash += 1

def is_moves_per_clash_maximal(self):
    return self._moves_per_clash == (settings.MAX_MOVES_PER_CLASH - 1)

def update_after_reconnect(self, game, player, opponent):
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

def update_moves_per_clash(self):
    self.decrement_turn_to_inc()
    if self.is_time_for_moves_per_clash_inc():
        self.reset_turns_to_inc()
        if not self.is_moves_per_clash_maximal():
            self.increment_moves_per_clash()

def update_game_stage(self):
    if self.get_game_stage() == GameStage.HUB:
        self.set_game_stage(GameStage.CLASH)
    else:
        self.set_game_stage(GameStage.HUB)

def limit_player_action_time(self, player_side):
    opp = self.get_opponent()
    g_u = self.get_game_user()
    id = opp.id if player_side == opp.conflict_side else g_u.id
    add_delayed_task(
        f'limit_action_time_{id}',
        settings.ACTION_MOVE_TIMEOUT,
        settings.ACTION_MOVE_TIMEOUT_FUNC
    )

def limit_player_reaction_time(self):
    add_delayed_task(
        f'limit_reaction_time_{self.get_opponent().id}',
        settings.REACTION_MOVE_TIMEOUT,
        settings.REACTION_MOVE_TIMEOUT_FUNC
    )

def limit_players_hub_time(self):
    print(f"limit_players_hub_time, player_id={self.get_game_user().id}")
    print(f"limit_players_hub_time, opp_id={self.get_opponent().id}")
    add_delayed_task(
        f'limit_hub_time_{self.get_game_user().id}',
        settings.HUB_STAGE_TIMEOUT,
        settings.HUB_STAGE_TIMEOUT_FUNC
    )
    add_delayed_task(
        f'limit_hub_time_{self.get_opponent().id}',
        settings.HUB_STAGE_TIMEOUT,
        settings.HUB_STAGE_TIMEOUT_FUNC
    )

def decrease_action_moves(self):
    self._moves_table[0] -= 1

def decrease_reaction_moves(self):
    self._moves_table[1] -= 1

def init_table_for_new_clash(self):
    self._update_moves_per_clash()
    for i in range(2):
        self._moves_table[i] = self._moves_per_clash

async def refresh_game_user(self):
    game_user_id = self.get_game_user().id
    refreshed_game_user = await get_game_user(game_user_id)
    self.set_game_user(refreshed_game_user)

async def refresh_game(self):
    game_id = self.get_game().id
    refreshed_game = await get_game(game_id)
    self.set_game(refreshed_game)

async def refresh_opponent(self):
    opp_id = self.get_opponent().id
    refreshed_opp = await get_game_user(opp_id)
    self.set_opponent(refreshed_opp)

async def decode_json(self, text_data):
    try:
        json_data = json.loads(text_data)
        self.set_valid_json_sent(True)
        return json_data
    except json.JSONDecodeError:
        await self.error("Wrong format of sent json")
