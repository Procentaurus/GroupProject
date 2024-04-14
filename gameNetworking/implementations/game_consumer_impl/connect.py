from gameNetworking.models.queries import *
from .main_game_loop.common import *

class Connector:

    def __init__(self, consumer):
        self._consumer = consumer
        self._opp = None
        self._game = None
        self._g_u = None

    async def connect(self):
        await self._consumer.accept()
        if not self._verify_connection():
            await self._consumer.close()
            return

        await self._initialize_game_user()
        num_t = await get_number_of_waiting_players("teacher")
        num_s = await get_number_of_waiting_players("student")

        if num_t > 0 and num_s > 0:
            await self._initialize_game_networking()
            await self._send_game_info_to_players()
            mng = InitCardsManager(self._consumer)
            await mng.manage_cards()
            # await initialize_game_archive()

    async def _initialize_game_networking(self):
        await self._set_opponent()

        game = await self._create_game()
        self._game = game
        await self._set_users_in_game()

        await self._add_players_channels_to_group(game.id)
        self._consumer.set_opponent_channel_name(self._opp.channel_name)

    async def _send_game_info_to_players(self):
        i_s = InfoSender(self._consumer)
        await i_s._send_game_creation_info_to_opp(self._game.id, self._g_u.id)
        await i_s._send_game_start_info()
        await i_s._send_game_start_info_to_opp(self._opp)

    def _get_access_token(self):
        return self._consumer.scope.get("token")
    
    def _get_conflict_side(self):
        return self._consumer.scope["url_route"]["kwargs"]["conflict_side"]

    def _is_access_token_valid(self):
        a_t = self._get_access_token()
        if a_t is None:
            return False if a_t is None else True
        
    def _is_conflict_side_valid(self):
        c_s = self._get_conflict_side()
        return True if (c_s == "teacher" or c_s == "student") else False
        
    async def _verify_connection(self):
        e_s = ErrorSender(self._consumer)
        c_s = self._get_conflict_side()
        if not self._is_access_token_valid():
            await e_s.send_invalid_token_info(c_s)
            return False

        if not self._is_conflict_side_valid():
            await e_s.send_invalid_conflict_side_info(c_s)
            return False
        
        return True
    
    async def _initialize_game_user(self):
        a_t = self._get_access_token()
        c_s = self._get_conflict_side()
        g_u = await create_game_user(a_t, c_s, self._consumer.channel_name)
        self._consumer.set_game_user(g_u)
        self._g_u = g_u
        # await delete_game_token(game_user)

    async def _set_opponent(self):
        opp = None
        if self._get_conflict_side() == "teacher":
            opp = await get_longest_waiting_player("student")
        else:
            opp = await get_longest_waiting_player("teacher")

        # Added as Connector field  because needed in later initialization
        self._opp = opp

        # Added as consumer field as needed in later game
        self._consumer.set_opponent(opp)

    async def _create_game(self):
        game = await create_game(self._g_u, self._opp)
        self._consumer.set_game_id(game.id)
        self._consumer.logger.info("The game has started.")
        return game

    async def _add_players_channels_to_group(self, game_id):
        await self._consumer.channel_layer.group_add(
            f"game_{game_id}", self._opp.channel_name)
        await self._consumer.channel_layer.group_add(
            f"game_{game_id}", self._g_u.channel_name)

    async def _send_game_creation_info_to_opponent(self, game_id):
        await self._consumer.send_message_to_opponent(
            {"game_id": str(game_id),
            "channel_name": self._consumer.channel_name},
            "game_creation")
   
    async def _send_game_start_info_to_players(self):
        await self._consumer.send_message_to_opponent(
            {"initial_money_amount" : self._opp.money,
            "initial_morale" : self._opp.morale},
            "game_start")
        
        await self._consumer.game_start(
            {"initial_money_amount" : self._g_u.money,
            "initial_morale" : self._g_u.morale})

    async def _set_users_in_game(self):
        (await self._g_u.get_user()).set_in_game()
        (await self._opp.get_user()).set_in_game()
