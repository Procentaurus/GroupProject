from gameMechanics.scripts.initial_shop import get_initial_shop_for_player

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
        await self._consumer.error(f"Cards: {data} do not exist")

    async def send_cards_not_in_shop_info(self, cards, log_cards_data):
        side = self._consumer.get_game_user().conflict_side
        await self._consumer.complex_error(
            f"Cards: {log_cards_data} are not in shop",
            f"Cards: {log_cards_data} are not in shop of {side} player",
            {"cards": cards}
        )

    async def send_card_not_owned_info(self, cards, log_cards_data):
        side = self._consumer.get_game_user().conflict_side
        await self._consumer.complex_error(
            f"Cards: {log_cards_data} are not owned",
            f"Cards: {log_cards_data} are not owned by {side} player",
            {"cards": cards}
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


async def send_card_sets_to_shop(consumer):
  
    initial_reaction_cards_for_teacher, initial_action_cards_for_teacher = (
        await get_initial_shop_for_player(5, 2, "teacher")
    )
    initial_reaction_cards_for_student, initial_action_cards_for_student = (
        await get_initial_shop_for_player(5, 2, "student")
    )

    if consumer.get_game_user():
        await send_cards_to_player(consumer, initial_action_cards_for_teacher,
            initial_reaction_cards_for_teacher)
        await send_cards_to_opponent(consumer, initial_action_cards_for_student,
            initial_reaction_cards_for_student)
    else:
        await send_cards_to_player(consumer, initial_action_cards_for_student,
            initial_reaction_cards_for_student)
        await send_cards_to_opponent(consumer, initial_action_cards_for_teacher,
            initial_reaction_cards_for_teacher)


async def send_cards_to_opponent(consumer, action_cards, reaction_cards):
    await consumer.send_message_to_opponent(
        {"action_cards" : action_cards,
        "reaction_cards" : reaction_cards},
        "card_package")
    
async def send_cards_to_player(consumer, action_cards, reaction_cards):
    await consumer.card_package(
        {"action_cards" : action_cards,
        "reaction_cards" : reaction_cards})
