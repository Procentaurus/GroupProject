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

    async def send_improper_move_info(self):
        side = self._consumer.get_game_user().conflict_side
        await self._consumer.error("Improper move made",
            f"Improper move made by {side} player")
        
    async def _send_wrong_message_type_info(self):
        await self._consumer.error(
            f"Wrong message type in the {self._consumer.get_game_stage()}"
            +" game stage.")
        
    async def _send_invalid_token_info(self, conflict_side):
        await self.consumer.error("You have used invalid token",
            f"Invalid authentication token used by {conflict_side} player")
        
    async def _send_invalid_conflict_side_info(self, conflict_side):
        await self.consumer.error("You have chosen invalid conflict side",
            f"Invalid conflict side chosen by {conflict_side} player")
        

class InfoSender:

    def __init__(self, consumer):
        self._consumer = consumer

    async def _send_game_creation_info_to_opp(self, game_id):
        await self._consumer.send_message_to_opponent(
            {"game_id": str(game_id),
            "channel_name": self._consumer.channel_name},
            "game_creation")
        
    async def _send_game_start_info_to_players(self):
        await self._consumer.send_message_to_opponent(
            {"initial_money_amount" : self._opponent.money,
            "initial_morale" : self._opponent.morale},
            "game_start")
        
        g_u = self._consumer.get_game_user()
        await self._consumer.game_start(
            {"initial_money_amount" : g_u.money,
            "initial_morale" : g_u.morale})
        
    


async def check_action_move_can_be_performed(consumer, game):
    
    if not await check_is_player_turn(consumer, game): return

    game_user = consumer.get_game_user()
    if game.next_move_type != "action":
        await consumer.error(
            "Wrong move. It is time for reaction.",
            f"{game_user.conflict_side} player performed move of wrong type.")
        return False
    
    # Check if player is in the clash stage, if not then flow error occured
    if game_user.state != PlayerState.IN_CLASH:
        await consumer.critical_error(
            f"Improper state {game_user.state} of {game_user.conflict_side} \
            player in clash action move.")
        return False
    
    return True

async def check_reaction_move_can_be_performed(
    consumer, game, reaction_cards_data):

    if not await check_is_player_turn(consumer, game): return

    game_user = consumer.get_game_user()
    if game.next_move_type != "reaction":
        await consumer.error(
            "Wrong move. It is time for action.",
            f"{game_user.conflict_side} player performed move of wrong type.")
        return False
    
    # Check if player is in the clash stage, if not then flow error occured
    if game_user.state != PlayerState.IN_CLASH \
        and game_user.state != PlayerState.AWAIT_CLASH_END:
        await consumer.critical_error(
            f"Improper state {game_user.state} of {game_user.conflict_side} \
            player in clash action move.")
        return False
    
    reaction_cards_ids = {x.get("reaction_card_id") for x in reaction_cards_data}
    reaction_card_exist = await check_all_reaction_cards_exist(
        consumer, reaction_cards_ids)
    if not reaction_card_exist: return False

    reaction_cards_are_owned = await check_game_user_own_reaction_cards(
        consumer, reaction_cards_data)
    if not reaction_cards_are_owned: return False

    return True

async def check_winner(
    consumer, opponent, new_player_morale, new_opponent_morale):
    
    game_user = consumer.get_game_user()
    if new_opponent_morale <= 0:
        consumer.set_winner(game_user.get_conflict_side())
        await announce_winner(consumer)
        return True
    elif new_player_morale <= 0:
        consumer.set_winner(opponent.get_conflict_side())
        await announce_winner(consumer, opponent)
        return True
    else: 
        return False
    
async def announce_winner(consumer):
    consumer.set_closure_from_user_side(False)
    await consumer.send_message_to_group(
        {"winner" : consumer.__winner},
        "game_end")
    
async def check_is_player_turn(consumer, game):
    game_user = consumer.get_game_user()
    if game.next_move_player != game_user.conflict_side:
        await consumer.error("Not your turn.",
            f"{game_user.conflict_side} player performed move \
            while it was not his turn.")
        return False
    return True

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