from gameMechanics.scripts.basic_mechanics import get_new_morale

from gameNetworking.enums import MessageType, PlayerState
from .common import SurrenderMoveHandler
from .abstract import MoveHandler, StageHandler
from .checkers import *


class ClashStageHandler(StageHandler):

    def __init__(self, consumer, game, message_type, data):
        super().__init__(consumer, game, message_type, data)

    async def perform_stage(self):
        if self._message_type == MessageType.PURCHASE_MOVE:
            p_m_h = ActionMoveHandler(self._consumer, self._game, self._data)
            await p_m_h.perform_move()
        elif self._message_type == MessageType.READY_MOVE:
            r_m_h = ReactionMoveHandler(self._consumer, self._game, self._data)
            await r_m_h.perform_move()
        elif self._message_type == MessageType.SURRENDER_MOVE:
            s_m_h = SurrenderMoveHandler(self._consumer)
            await s_m_h.perform_move()
        else:
            e_s = ErrorSender(self._consumer)
            await e_s.send_wrong_message_type_info()


class ActionMoveHandler(MoveHandler):

    def __init__(self, consumer, game, data):
        super().__init__(consumer)
        self._game = game
        self._a_card = data.get("action_card_id")

    async def _perform_move_mechanics(self):
        game_user = self._consumer.get_game_user()
        await game_user.remove_action_card(self._a_card)
        await self._consumer.send_message_to_opponent(
            {"action_card" : self._a_card},
            "opponent_move")
    
        self._consumer.decrease_action_moves()
        if self._consumer.no_action_moves_left():
            await game_user.set_state(PlayerState.AWAIT_CLASH_END)

    async def _verify_move(self):
        
        g_v = GameVerifier(self._consumer, self._game)
        if not await g_v.verify_next_move_performer(): return
        if not await g_v.verify_game_next_move_type(): return
        
        p_v = PlayerVerifier(self._consumer)
        if not await p_v.verify_player_in_clash(): return False

        a_c_c = ActionCardsChecker([self._a_card])
        c_v = CardVerifier(self._consumer, a_c_c)
        if not a_c_c.is_cards_data_empty(): return False
        if not await c_v.verify_cards_for_clash(): return False

        if not await g_v.verify_turn_update_successful(): return


class ReactionMoveHandler(MoveHandler):
    def __init__(self, consumer, game, message_type, data):
        super().__init__(consumer, game, message_type, data)

async def clash_reaction_move_mechanics(consumer, game, reaction_cards_data):
    
    if not await check_reaction_move_can_be_performed(
        consumer, game, reaction_cards_data): return

    if not game.update_after_turn():
        await consumer.critical_error("Updating game turn impossible.")
        return

    moves_table = consumer.get_moves_table()
    moves_table[1] -= 1 # 1 is index of reaction moves

    opponent = await game.get_opponent_player(game_user)
    new_opp_morale, money_opp_gained, new_player_morale, money_player_gained = (
        await get_new_morale(
            game_user, opponent,
            consumer.get_action_card_played_by_opponent, reaction_cards_data)
    )
    action_cards_player_gained, action_cards_opp_gained = None, None
    reaction_cards_player_gained, reaction_cards_opp_gained = None, None

    await consumer.send_message_to_opponent(
        {"reaction_cards" : reaction_cards_data},
        "opponent_move")
    
    game_user = consumer.get_game_user()
    there_is_winner = await check_winner(
        consumer, opponent, new_player_morale, new_opp_morale)
    if there_is_winner: return

    game_user_message_body = create_clash_result_response_body(
        new_player_morale,  new_opp_morale, money_player_gained,
        action_cards_player_gained, reaction_cards_player_gained)
    await consumer.clash_result(game_user_message_body)

    opp_message_body = create_clash_result_response_body(
        new_opp_morale,  new_player_morale, money_opp_gained,
        action_cards_opp_gained, reaction_cards_opp_gained)
    await consumer.send_message_to_opponent(opp_message_body,"clash_result")

    await add_gains_to_account(
        new_player_morale, money_player_gained,
        action_cards_player_gained, reaction_cards_player_gained)
    await add_gains_to_account(
        opponent, new_opp_morale, money_opp_gained,
        action_cards_opp_gained, reaction_cards_opp_gained)
    
    await remove_all_used_reaction_cards(game_user, reaction_cards_data)

    if player_has_no_more_action_moves(moves_table) \
        and player_has_no_more_reaction_moves(moves_table):
           
        if opponent.state == PlayerState.AWAIT_CLASH_END:
            new_clash_initiated = consumer.init_table_for_new_clash()
            if not new_clash_initiated: return

            await consumer.send_message_to_group({}, "clash_end")
        else:
            await inform_about_improper_state_error(consumer, "reaction_move")

async def add_gains_to_account(
    user, new_morale, money_gained, action_cards_gained, reaction_cards_gained):

    await user.set_morale(new_morale)
    await user.add_money(money_gained)
    
    for action_card in action_cards_gained:
        await user.add_action_card(action_card)

    for reaction_card_data in reaction_cards_gained:
        await user.add_reaction_card(
            reaction_card_data.get("reaction_card_id"),
            reaction_card_data.get("amount"))

def create_clash_result_response_body(new_morale, new_opponent_morale,
    money_gained, action_cards_gained, reaction_cards_gained):
    return {
        "new_player_morale" : new_morale,
        "new_opponent_morale" : new_opponent_morale,
        "money_gained" : money_gained,
        "action_cards_gained" : action_cards_gained,
        "reaction_cards_gained" : reaction_cards_gained
    }

def player_has_no_more_action_moves(moves_table):
    return moves_table[0] == 0

def player_has_no_more_reaction_moves(moves_table):
    return moves_table[1] == 0

async def remove_all_used_reaction_cards(game_user, reaction_cards_data):
    for reaction_card_data in reaction_cards_data:
        await game_user.remove_reaction_card(
            reaction_card_data.get("reaction_card_id"),
            reaction_card_data.get("amount"))
