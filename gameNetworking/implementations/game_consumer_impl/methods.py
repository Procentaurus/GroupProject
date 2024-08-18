import json
from channels.exceptions import StopConsumer
from django.conf import settings

from WebGame.loggers import get_game_logger

from ...enums import GameStage
from ...models.queries import get_game_user, get_game
from ...messager.scheduler import add_delayed_task
from .connect import Connector
from .disconnect import Disconnector
from .main_game_loop.main_game_loop import GameLoopHandler


def reset_turns_to_inc(self):
    self._turns_to_inc = (settings.TURNS_BETWEEN_NUM_MOVES_INC - 1)
    self.logger.info(f"User({self._game_user.user_id}) has turns to next "
                     f" incrementation number reset: {self._turns_to_inc}")

def decrement_turn_to_inc(self):
    self._turns_to_inc -= 1
    self.logger.info(f"User({self._game_user.user_id}) has turns to next "
                     f" incrementation number decreased: {self._turns_to_inc}")

def increment_moves_per_clash(self):
    self._moves_per_clash += 1
    self.logger.info(f"User({self._game_user.user_id}) has turns to next "
                     f" incrementation number increased: {self._turns_to_inc}")

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
    self.logger.info(f"The number of moves per clash has been updated for "
                    f"User({self._opponent.user_id}): {self._moves_per_clash}")

def update_game_stage(self):
    if self.get_game_stage() == GameStage.HUB:
        self.set_game_stage(GameStage.CLASH)
    else:
        self.set_game_stage(GameStage.HUB)
    self.logger.info(f"The game stage has been updated for "
                     f"User({self._opponent.user_id}): {self._game_stage}")

def limit_player_action_time(self, player):
    add_delayed_task(
        f'limit_action_time_{player.id}',
        settings.ACTION_MOVE_TIMEOUT,
        settings.ACTION_MOVE_TIMEOUT_FUNC
    )
    self.logger.info(f"The delayed action move has been added for "
                f"User({player.user_id})")

def limit_opponent_reaction_time(self):
    add_delayed_task(
        f'limit_reaction_time_{self._opponent.id}',
        settings.REACTION_MOVE_TIMEOUT,
        settings.REACTION_MOVE_TIMEOUT_FUNC
    )
    self.logger.info(f"The delayed reaction move has been added for "
                    f"User({self._opponent.user_id})")

def limit_player_hub_time(self, player):
    add_delayed_task(
        f'limit_hub_time_{player.id}',
        settings.HUB_STAGE_TIMEOUT,
        settings.HUB_STAGE_TIMEOUT_FUNC
    )
    self.logger.info(f"The delayed ready move has been added for "
                      f"User({self._game_user.user_id})")

def decrease_action_moves(self):
    self._moves_table[0] -= 1
    self.logger.info(f"User({self._game_user.user_id}) has action move number "
                     f"decreased: {self._moves_table[0]}")

def decrease_reaction_moves(self):
    self._moves_table[1] -= 1
    self.logger.info(f"User({self._game_user.user_id}) has reaction move number "
                     f"increased: {self._moves_table[1]}")

def init_table_for_new_clash(self):
    self._update_moves_per_clash()
    for i in range(2):
        self._moves_table[i] = self._moves_per_clash
    self.logger.info(f"User({self._game_user.user_id}) has move table updated: "
                     f"{self._moves_table}")

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

def activate_logger(self):
    self.logger = get_game_logger(str(self._game.id))

async def decode_json(self, text_data):
    try:
        json_data = json.loads(text_data)
        self.set_valid_json_sent(True)
        return json_data
    except json.JSONDecodeError:
        await self.error("Wrong format of sent json")

async def connect(self):
    connector = Connector(self)
    await connector.connect()

async def disconnect(self, *args):
    disconnector = Disconnector(self)
    await disconnector.disconnect()           
    raise StopConsumer()

async def receive_json(self, data):
    loop_handler = GameLoopHandler(self, data)
    await loop_handler.perform_game_loop()
    self.set_valid_json_sent(False)

async def send_message_to_group(self, data, event):
    await self.channel_layer.group_send(
        f"game_{self._game.id}",
        {
            'type': event,
            **data,
        }
    )

async def send_message_to_opponent(self, data, event):
    await self.channel_layer.send(
        self._opponent.channel_name,
        {
            'type': event,
            **data,
        }
    )
