from gameMechanics.serializers import *

from ...scheduler.scheduler import remove_delayed_task, update_game_user_state
from ...scheduler.scheduler import add_delayed_task
from ...scheduler.scheduler import verify_task_exists
from ...models.queries import *
from ...models.game.serializers import GameReconnectSerializer
from ...models.game_user.serializers import GameUserReconnectSerializer
from ...enums import GameStage, PlayerState
from .main_game_loop.common import *


class Connector:

    def __init__(self, consumer):
        self._consumer = consumer
        self._user = consumer.scope.get("user")
        self._side = consumer.scope["url_route"]["kwargs"]["conflict_side"]

    async def connect(self):
        await self._consumer.accept()
        if not self._verify_connection():
            await self._consumer.close()
        await self._make_connection()

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
    
    async def _make_connection(self):

        async def retrieve_saved_game_data():
            game_user = await get_game_user_with_user(self._user)
            if game_user is not None:
                game = await get_game_with_game_user(game_user)
                if game is not None:
                    opponent = await game.get_opponent_player(game_user)
                    if opponent is not None:
                        return game_user, game, opponent
            return None, None, None

        def is_saved_game_data_available(game_user, game, opponent):
            if game_user is None or game is None or opponent is None:
                return False
            else: return True

        game_user, game, opponent = await retrieve_saved_game_data()
        if is_saved_game_data_available(game_user, game, opponent):
            await self._connect_to_saved_game(game_user, game, opponent)
        else:
            await self._connect_to_new_game()

    async def _connect_to_new_game(self):
         # TODO usuwać game token -> await delete_game_token(game_user)
        game_user = await self._create_game_user()
        self._consumer.set_game_user(game_user)
        num_t = await get_number_of_waiting_players("teacher")
        num_s = await get_number_of_waiting_players("student")
        if num_t > 0 and num_s > 0:
            opponent = await self._find_opponent()
            game = await self._create_game(game_user, opponent)
            self._consumer.set_game(game)
            self._consumer.set_opponent(opponent)
            # TODO ustawić in_game status -> await self._set_in_game_status()
            await self._add_players_channels_to_group(game)
            await self._send_initial_game_info_to_players(game, game_user)
            await self._init_shop_for_game()
            self._consumer.limit_players_hub_time()
            self.init_queue_with_game_user_states(
                str(game.id),
                str(game_user.id),
                str(opponent.id)
            )

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

    async def _send_initial_game_info_to_players(self, game, game_user):
        i_i_s = InitInfoSender(self._consumer)
        await i_i_s._send_game_creation_info_to_opp(game.id, game_user.id)
        await i_i_s._send_game_start_info()
        await i_i_s._send_game_start_info_to_opp(self._consumer.get_opponent())

    async def _init_shop_for_game(self):
        mng = InitCardsManager(self._consumer)
        await mng.manage_cards()

    async def _connect_to_saved_game(self, player, game, opponent):
        await player.update_channel_name(self._consumer.channel_name)
        self._consumer.update_after_reconnect(game, player, opponent)
        if verify_task_exists(f'limit_opponent_rejoin_time_{opponent.id}'):
            remove_delayed_task(f'limit_opponent_rejoin_time_{opponent.id}')
            remove_delayed_task(f'limit_game_data_lifetime_{game.id}')
            await self._consumer.refresh_opponent()
            opponent = self._consumer.get_opponent()
            await self._add_players_channels_to_group(game)
            await self._consumer.game_reconnect(
                await self._create_reconnect_message_body(player, game)
            )
            await self._consumer.send_message_to_opponent(
                await self._create_reconnect_message_body(opponent, game),
                'game_reconnect'
            )
            self._reactivate_all_game_tasks(game)
            await self._inform_players_about_reactivated_tasks(game, opponent)
        else:
            remove_delayed_task(f'limit_game_data_lifetime_{game.id}')
            await self._consumer.opponent_rejoin_waiting()
            add_delayed_task(
                f'limit_opponent_rejoin_time_{player.id}',
                settings.REJOIN_TIMEOUT,
                settings.REJOIN_TIMEOUT_FUNC
            )
            await game.clear_backup_status()

    async def _create_reconnect_message_body(self, player, game):

        async def get_serialized_owned_a_cards(player):
            action_cards_owned = []
            for card in await player.get_owned_action_cards():
                action_cards_owned.append(ActionCardDataSerializer(card).data)
            return action_cards_owned

        async def get_serialized_owned_r_cards(player):
            reaction_cards_owned = []
            for card_data in await get_owned_reaction_cards(player):
                reaction_cards_owned.append({
                    'card': ReactionCardDataSerializer(card_data['card']).data,
                    'amount': card_data['amount']
                })
            return reaction_cards_owned

        async def get_serialized_a_cards_in_shop(player):
            action_cards_in_shop = []
            for card in await player.get_action_cards_in_shop():
                action_cards_in_shop.append(ActionCardDataSerializer(card).data)
            return action_cards_in_shop

        async def get_serialized_r_cards_in_shop(player):
            reaction_cards_in_shop = []
            for card_data in await get_reaction_cards_in_shop(player):
                reaction_cards_in_shop.append({
                    'card': ReactionCardDataSerializer(card_data['card']).data,
                    'amount': card_data['amount']
                })
            return reaction_cards_in_shop

        body = {
            'type': 'game_reconnect',
            'game_data': GameReconnectSerializer(game).data,
            'player': GameUserReconnectSerializer(player).data,
            'owned_action_cards': await get_serialized_owned_a_cards(player),
            'reaction_cards_owned': await get_serialized_owned_r_cards(player)
        }
        if self._consumer.get_game_stage() == GameStage.HUB:
            body['action_cards_in_shop'] = await get_serialized_a_cards_in_shop(
                                                player)
            body['reaction_cards_in_shop'] = await get_serialized_r_cards_in_shop(
                                                    player)
        return body
    
    async def _inform_players_about_reactivated_tasks(self, game, opponent):
        for task_data, task_time in game.delayed_tasks.items():
            _, task_id = task_data.rsplit('_', 1)
            if task_id == str(opponent.id):
                await self._consumer.send_message_to_opponent(
                    {"time_remaining": int(task_time)},
                    'time_info'
                )
            else:
                await self._consumer.time_info({
                    "time_remaining": int(task_time)
                })

    def _reactivate_all_game_tasks(self, game):
        for task_data, task_time in game.delayed_tasks.items():
            task_func, _ = task_data.rsplit('_', 1)
            add_delayed_task(
                task_data,
                int(task_time),
                settings.TIMEOUT_MODULE + '.' + str(task_func),
            )

    async def _set_in_game_status(self, game_user):
        (await game_user.get_user()).set_in_game()

    async def _add_players_channels_to_group(self, game):
        await self._consumer.channel_layer.group_add(
            f"game_{game.id}", self._consumer.get_opponent().channel_name
        )
        await self._consumer.channel_layer.group_add(
            f"game_{game.id}", self._consumer.get_game_user().channel_name
        )

    def init_queue_with_game_user_states(self, game_id, player_id, opponent_id):
        update_game_user_state(game_id, player_id, PlayerState.IN_HUB)
        update_game_user_state(game_id, opponent_id, PlayerState.IN_HUB)
