from ...scheduler.scheduler import remove_delayed_task, add_delayed_task
from ...models.queries import *
from .main_game_loop.common import *


class Connector:

    def __init__(self, consumer):
        self._consumer = consumer
        self._game = None
        self._user = consumer.scope.get("user")
        self._side = consumer.scope["url_route"]["kwargs"]["conflict_side"]

    async def connect(self):

        def is_saved_game_data_available(game_user, game, opponent):
            if game_user is None or game is None or opponent is None:
                return False
            else: True

        await self._consumer.accept()
        if not self._verify_connection():
            await self._consumer.close()
            return

        game_user, game, opponent = await self._retrieve_saved_game_data()
        if is_saved_game_data_available(game_user, game, opponent):
            await self._connect_to_saved_game(game_user, game, opponent)
        else:
            await self._connect_to_new_game()

    async def _verify_connection(self):

        def is_token_valid(t):
            return True if t is not None else False

        def is_conflict_side_valid(c_s):
            return True if (c_s == "teacher" or c_s == "student") else False

        e_s = ErrorSender(self._consumer)
        c_s = self._consumer.scope["url_route"]["kwargs"]["conflict_side"]
        t = self._consumer.scope.get("token")
        if not is_token_valid(t):
            await e_s.send_invalid_token_info(c_s)
            return False

        if not is_conflict_side_valid(c_s):
            await e_s.send_invalid_conflict_side_info(c_s)
            return False

        return True

    async def _retrieve_saved_game_data(self):
        game_user = await get_game_user_with_user(self._user)
        if game_user is not None:
            game = await get_game_with_game_user(game_user)
            if game is not None:
                opponent = await game.get_opponent_player()
                return game_user, game, opponent
        return None, None, None

    async def _connect_to_new_game(self):
        # await delete_game_token(game_user)
        game_user = await self._create_game_user()
        self._consumer.set_game_user(game_user)
        num_t = await get_number_of_waiting_players("teacher")
        num_s = await get_number_of_waiting_players("student")
        if num_t > 0 and num_s > 0:
            opponent = await self._find_opponent()
            game = await self._create_game(game_user, opponent)
            self._game = game
            self._init_consumer_data(game, opponent)
            # await self._set_in_game_status()
            await self._add_players_channels_to_group(game.id)
            await self._send_initial_game_info_to_players()
            await self._init_shop_for_game()
            self._consumer.limit_players_hub_time()

    async def _create_game_user(self):
        game_user = await create_game_user(
            self._user,
            self._side, 
            self._consumer.channel_name
        )
        self._consumer.logger.info(
            f"The game_user for user {self._user.username} has been created."
        )
        return game_user

    async def _find_opponent(self):
        if self._side == "teacher":
            return await get_longest_waiting_player("student")
        else:
            return await get_longest_waiting_player("teacher")

    async def _create_game(self, game_user, opponent):
        if self._side == "teacher":
            game = await create_game(game_user, opponent)
        else:
            game = await create_game(opponent, game_user)
        self._consumer.logger.info("The game has been created.")
        return game

    async def _send_initial_game_info_to_players(self):
        i_s = InfoSender(self._consumer)
        await i_s._send_game_creation_info_to_opp(
            self._game.id, self._consumer.get_game_user().id
        )
        await i_s._send_game_start_info()
        await i_s._send_game_start_info_to_opp(self._consumer.get_opponent())

    async def _init_shop_for_game(self):
        mng = InitCardsManager(self._consumer)
        await mng.manage_cards()

    async def _connect_to_saved_game(self, game_user, game, opponent):
        await game_user.update_channel_name(self._consumer.channel_name)
        self._consumer.set_game_user(game_user)
        self._init_consumer_data(game, opponent)
        if True: # jest task na rejoin
            remove_delayed_task(f'limit_opponent_rejoin_time_{opponent.id}')
            self._add_players_channels_to_group(game.id)
            # wymiana channel name'ów
            # message game_reconnect wraz z danymi każdego z graczy
        else:
            remove_delayed_task(f'limit_game_data_lifetime_{game.id}')
            await self._consumer.rejoin_waiting()
            add_delayed_task(f'limit_opponent_rejoin_time_{game_user.id}')





    async def _set_in_game_status(self, game_user):
        (await game_user.get_user()).set_in_game()

    async def _add_players_channels_to_group(self, game_id):
        await self._consumer.channel_layer.group_add(
            f"game_{game_id}", self._consumer.get_opponent().channel_name
        )
        await self._consumer.channel_layer.group_add(
            f"game_{game_id}", self._consumer.get_game_user().channel_name
        )

    def _init_consumer_data(self, game, opponent):
        self._consumer.set_game_id(game.id)
        self._consumer.set_opponent(opponent)
        self._consumer.set_opponent_channel_name(opponent.channel_name)
