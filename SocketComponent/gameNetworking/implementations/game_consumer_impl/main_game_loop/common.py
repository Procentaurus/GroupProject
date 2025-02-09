from django.conf import settings

from gameMechanics.hubMechanics.shop import get_shop_for_player

from ....models.queries import add_reaction_card_to_shop
from ....messager.scheduler import check_game_user_state
from .abstract import MoveHandler


class SurrenderMoveHandler(MoveHandler):

    def __init__(self, consumer):
        super().__init__(consumer)

    async def _verify_move(self):
        return True

    async def _perform_move_mechanics(self, is_delayed):
        g_u = self._consumer.get_game_user()
        winner_side = await self._get_winner_side(g_u)
        await self._consumer.send_message_to_group(
            {"winner" : winner_side, "after_surrender" : True},
            "game_end")
        self.logger.info(f"User({g_u.user_id})({g_u.conflict_side})"
                    " has surrendered")

    async def _get_winner_side(self, g_u):
        return "student" if g_u.is_teacher() else "teacher"


class ErrorSender:

    def __init__(self, consumer):
        self._consumer = consumer

    async def send_invalid_data_structure_info(self):
        await self._consumer.error("Invalid format of sent data")

    async def send_cards_not_exist_info(self, data):
        g_u = self._consumer.get_game_user()
        await self._consumer.complex_error(
            f"Some of chosen cards do not exist",
            f"User({g_u.user_id})({g_u.conflict_side}) tried to use cards that "
            + " do not exist",
            {"not_existing_cards" : data}
        )

    async def send_cards_not_in_shop_info(self, cards):
        g_u = self._consumer.get_game_user()
        await self._consumer.complex_error(
            f"Some of chosen cards are not in shop",
            f"User({g_u.user_id})({g_u.conflict_side}) tried to buy cards that "
            + " are not in shop",
            {"cards_not_in_shop": cards}
        )

    async def send_card_not_owned_info(self, cards):
        g_u = self._consumer.get_game_user()
        await self._consumer.complex_error(
            f"Some of chosen cards are not owned",
            f"User({g_u.user_id})({g_u.conflict_side}) tried to use cards he "
            + "doesn't own",
            {"cards_not_owned": cards}
        )

    async def send_improper_state_error(self, move_type):
        game_user = self._consumer.get_game_user()
        game_id = self._consumer.get_game().id
        state = check_game_user_state(str(game_id), str(game_user.id))
        await self._consumer.critical_error(
            f"Improper state: {state} of User({game_user.user_id})"
            f"({game_user.conflict_side}) in {move_type}")

    async def send_not_enough_money_info(self):
        g_u = self._consumer.get_game_user()
        await self._consumer.error(
            "Do not have enough money to buy chosen cards",
            f"User({g_u.user_id})({g_u.conflict_side}) don't have enough money "
            + "to buy"
            " chosen cards")

    async def send_improper_move_info(self, add_msg):
        g_u = self._consumer.get_game_user()
        await self._consumer.error(f"Improper move made - {add_msg}",
            f"User({g_u.user_id})({g_u.conflict_side}) made the improper move")

    async def send_wrong_message_type_info(self):
        await self._consumer.error(
            f"Wrong message type in the {self._consumer.get_game_stage()}"
            " game stage.")

    async def send_invalid_token_info(self, conflict_side):
        await self.consumer.error("You have used invalid token",
            f"Invalid authentication token used by {conflict_side} player")

    async def send_invalid_conflict_side_info(self, conflict_side):
        await self.consumer.error("You have chosen invalid conflict side",
            f"Invalid conflict side chosen by {conflict_side} player")

    async def send_game_not_started_info(self, game_user):
        await self._consumer.error(
            f"User({game_user.user_id})({game_user.conflict_side}) made move "
            +" before the game has started")

    async def send_turn_update_fail_error(self):
        await self._consumer.critical_error("Updating game turn impossible.")


class InitInfoSender:

    def __init__(self, consumer):
        self._consumer = consumer

    async def _send_game_creation_info_to_opp(self, game_id, opp_id):
        await self._consumer.send_message_to_opponent(
            {"game_id": str(game_id),
            "opponent_id": str(opp_id)},
            "game_creation")

    async def _send_game_start_info_to_opp(self):
        opp = self._consumer.get_opponent()
        player = self._consumer.get_game_user()
        await self._consumer.send_message_to_opponent(
            {"initial_money_amount": opp.money,
            "initial_morale": opp.morale,
            "initial_reroll_price": opp.reroll_price,
            "opponent_id": str(player.user_id)},
            "game_start")

    async def _send_game_start_info(self):
        opp = self._consumer.get_opponent()
        g_u = self._consumer.get_game_user()
        await self._consumer.game_start(
            {"initial_money_amount" : g_u.money,
            "initial_morale" : g_u.morale,
            "initial_reroll_price": g_u.reroll_price,
            "opponent_id": str(opp.user_id)})


class InitShopCardsGetter:

    def __init__(self, game_user, num_a_cards, num_r_cards):
        self._g_u = game_user
        self._num_r_cards = num_r_cards
        self._num_a_cards = num_a_cards

    async def get_player_cards(self):
        conflict_side = "teacher" if self._g_u.is_teacher() else "student"
        return (await get_shop_for_player(
            self._num_a_cards, self._num_r_cards, conflict_side))[::-1]

    async def get_opponent_cards(self):
        conflict_side = "student" if self._g_u.is_teacher() else "teacher"
        return (await get_shop_for_player(
            self._num_a_cards, self._num_r_cards, conflict_side))[::-1]


class ShopCardsAdder:

    def __init__(self, user, a_cards, r_cards):
        self._user = user
        self._a_cards = a_cards if a_cards is not None else []
        self._r_cards = r_cards if r_cards is not None else []

    async def add_all_cards_shop(self):
        await self._add_all_a_cards_to_shop()
        await self._add_all_r_cards_to_shop()

    async def _add_all_a_cards_to_shop(self):
        if self._a_cards != []:
            cards_ids = [card['id'] for card in self._a_cards]
            for card_id in cards_ids:
                await self._user.add_action_card_to_shop(card_id)

    async def _add_all_r_cards_to_shop(self):
        if self._r_cards != []:
            purchase_data = [
                {"id": card_data["card"]["id"], "amount": card_data["amount"]}
                for card_data in self._r_cards
            ]
            for data in purchase_data:
                await add_reaction_card_to_shop(
                    self._user, data.get("id"), data.get("amount"))


class CardSender:

    def __init__(self, consumer, a_cards, r_cards):
        self._consumer = consumer
        self._a_cards = a_cards
        self._r_cards = r_cards

    async def send_cards_to_opponent(self):
        await self._consumer.send_message_to_opponent(
            {"action_cards": self._a_cards,
            "reaction_cards": self._r_cards},
            "card_package")

    async def send_cards_to_player(self):
        await self._consumer.card_package(
            {"action_cards": self._a_cards,
            "reaction_cards": self._r_cards})


class InitCardsManager:

    def __init__(self, consumer):
        self._consumer = consumer
        self._g_u = self._consumer.get_game_user()
        self._opp = self._consumer.get_opponent()
        self._player_a_cards = None
        self._player_r_cards = None
        self._opp_a_cards = None
        self._opp_r_cards = None

    async def manage_cards(self):
        await self._get_cards()
        await self._add_cards_to_shop()
        await self._send_cards()

    async def _get_cards(self):
        i_s_c_g = InitShopCardsGetter(
            self._g_u,
            settings.INIT_R_CARDS_NUMBER,
            settings.INIT_A_CARDS_NUMBER
        )
        (player_a_cards, player_r_cards) = await i_s_c_g.get_player_cards()
        self._player_a_cards = player_a_cards
        self._player_r_cards = player_r_cards

        (opp_a_cards, opp_r_cards) = await i_s_c_g.get_opponent_cards()
        self._opp_a_cards = opp_a_cards
        self._opp_r_cards = opp_r_cards

    async def _add_cards_to_shop(self):
        s_c_a = ShopCardsAdder(
            self._g_u, self._player_a_cards, self._player_r_cards)
        await s_c_a.add_all_cards_shop()
        s_c_a = ShopCardsAdder(
            self._opp, self._opp_a_cards, self._opp_r_cards)
        await s_c_a.add_all_cards_shop()

    async def _send_cards(self):
        c_s = CardSender(
            self._consumer,
            self._player_a_cards,
            self._player_r_cards
        )
        await c_s.send_cards_to_player()
        c_s = CardSender(
            self._consumer,
            self._opp_a_cards,
            self._opp_r_cards
        )
        await c_s.send_cards_to_opponent()
