from gameMechanics.scripts.initial_shop import get_initial_shop_for_player

from ....models.queries import add_reaction_card_to_shop
from .abstract import MoveHandler


class SurrenderMoveHandler(MoveHandler):

    def __init__(self, consumer):
        super().__init__(consumer)

    async def _verify_move(self):
        return True

    async def perform_move_mechanics(self):
        g_u = self._consumer.get_game_user()
        self._consumer.logger.info(
            f"{g_u.conflict_side} player has surrendered")
        winner = self._get_winner_side()
        self._consumer.set_winner(winner)
        self._consumer.set_closure_from_user_side(False)
        await self._send_game_end_info()

    async def _send_game_end_info(self, winner):
        await self._consumer.send_message_to_group(
            {"winner" : winner, "after_surrender" : True},
            "game_end")
        
    async def _get_winner_side(self):
        g_u = self._consumer.get_game_user()
        return "student" if await g_u.is_teacher() else "teacher"

    
class ErrorSender:

    def __init__(self, consumer):
        self._consumer = consumer

    async def send_invalid_data_structure_info(self):
        await self._consumer.error("Invalid format of sent data")

    async def send_cards_not_exist_info(self, data):
        side = self._consumer.get_game_user().conflict_side
        await self._consumer.complex_error(
            f"Some of chosen cards do not exist",
            f"{side} player tried to use cards that do not exist",
            {"not_existing_cards" : data}
        )


    async def send_cards_not_in_shop_info(self, cards):
        side = self._consumer.get_game_user().conflict_side
        await self._consumer.complex_error(
            f"Some of chosen cards are not in shop",
            f"{side} player tried to buy cards that are not in shop",
            {"cards_not_in_shop": cards}
        )

    async def send_card_not_owned_info(self, cards):
        side = self._consumer.get_game_user().conflict_side
        await self._consumer.complex_error(
            f"Some of chosen cards are not owned",
            f"{side} player tried to use cards that he doesnt own",
            {"cards_not_owned": cards}
        )

    async def send_improper_state_error(self, move_type):
        game_user = self._consumer.get_game_user()
        await self._consumer.critical_error(
            f"Improper state: {game_user.state} of {game_user.conflict_side}"
            + f" player in {move_type}.")
        
    async def send_not_enough_money_info(self):
        side = self._consumer.get_game_user().conflict_side
        await self._consumer.error(
            "Do not have enough money to buy chosen cards",
            f"Not enough money to buy cards by {side} player")

    async def send_improper_move_info(self, add_msg):
        side = self._consumer.get_game_user().conflict_side
        await self._consumer.error(f"Improper move made - {add_msg}",
            f"Improper move made by {side} player")
        
    async def send_wrong_message_type_info(self):
        await self._consumer.error(
            f"Wrong message type in the {self._consumer.get_game_stage()}"
            +" game stage.")
        
    async def send_invalid_token_info(self, conflict_side):
        await self.consumer.error("You have used invalid token",
            f"Invalid authentication token used by {conflict_side} player")
        
    async def send_invalid_conflict_side_info(self, conflict_side):
        await self.consumer.error("You have chosen invalid conflict side",
            f"Invalid conflict side chosen by {conflict_side} player")
        
    async def send_game_not_started_info(self, conflict_side):
        await self._consumer.error(
            f"{conflict_side} player made move before the game"
            +" has started")

    async def send_turn_update_fail_error(self):
        await self._consumer.critical_error("Updating game turn impossible.")


class InfoSender:

    def __init__(self, consumer):
        self._consumer = consumer

    async def _send_game_creation_info_to_opp(self, game_id):
        await self._consumer.send_message_to_opponent(
            {"game_id": str(game_id),
            "channel_name": self._consumer.channel_name},
            "game_creation")
        
    async def _send_game_start_info_to_opp(self, opp):
        await self._consumer.send_message_to_opponent(
            {"initial_money_amount" : opp.money,
            "initial_morale" : opp.morale},
            "game_start")
        
    async def _send_game_start_info(self):   
        g_u = self._consumer.get_game_user()
        await self._consumer.game_start(
            {"initial_money_amount" : g_u.money,
            "initial_morale" : g_u.morale})


class ShopCardsHandler:

    def __init__(self, consumer, opponent):
        self._consumer = consumer
        self._g_u = consumer.get_game_user()
        self._opp = opponent
        self._s_a_cards = None
        self._s_r_cards = None
        self._t_a_cards = None
        self._t_r_cards = None

    async def _get_cards(self):
        await self._get_student_cards(5, 2)
        await self._get_teacher_cards(5, 2)

    async def _get_teacher_cards(self, num_a_cards, num_r_cards):
        (a_cards, r_cards) = (await get_initial_shop_for_player(
            num_a_cards, num_r_cards, "teacher"))[::-1]
        
        self._t_a_cards = a_cards
        self._t_r_cards = r_cards
    
    async def _get_student_cards(self, num_a_cards, num_r_cards):
        (a_cards, r_cards) = (await get_initial_shop_for_player(
            num_a_cards, num_r_cards, "student"))[::-1]
        
        self._s_a_cards = a_cards
        self._s_r_cards = r_cards

    async def add_cards_to_shop(self):
        if not self._cards_already_got():
            await self._get_cards()

        await self._add_all_a_cards_to_shop(self._g_u)
        await self._add_all_a_cards_to_shop(self._opp)
        # await self._add_all_r_cards_to_shop(self._g_u)
        # await self._add_all_r_cards_to_shop(self._opp)
    
    async def _add_all_a_cards_to_shop(self, player):
        is_teacher = await player.is_teacher()
        cards = self._t_a_cards if is_teacher else self._s_a_cards

        cards_ids = [card['id'] for card in cards]
        for card_id in cards_ids:
            await player.add_action_card_to_shop(card_id)

    async def _add_all_r_cards_to_shop(self, player):
        is_teacher = await player.is_teacher()
        cards_data = self._t_r_cards if is_teacher else self._s_r_cards

        purchase_data = [
            {"id": card_data["card"]["id"], "amount": card_data["amount"]}
            for card_data in cards_data
        ]
        for data in purchase_data:
            await add_reaction_card_to_shop(
                self._g_u, data.get("id"), data.get("amount"))

    async def send_card_sets_to_shop(self):
        if not self._cards_already_got():
            await self._get_cards()

        if await self._g_u.is_teacher():
            await self._send_cards_to_player(self._t_a_cards, self._t_r_cards)
            await self._send_cards_to_opponent(self._s_a_cards, self._s_r_cards)
        else:
            await self._send_cards_to_player(self._s_a_cards, self._s_r_cards)
            await self._send_cards_to_opponent(self._t_a_cards, self._t_r_cards)

    async def _send_cards_to_opponent(self, a_cards, r_cards):
        await self._consumer.send_message_to_opponent(
            {"action_cards" : a_cards,
            "reaction_cards" : r_cards},
            "card_package")
        
    async def _send_cards_to_player(self, a_cards, r_cards):
        await self._consumer.card_package(
            {"action_cards" : a_cards,
            "reaction_cards" : r_cards})
        
    def _cards_already_got(self):
        return (self._s_a_cards is not None and self._s_r_cards is not None 
            and self._t_a_cards is not None and self._t_r_cards is not None)
