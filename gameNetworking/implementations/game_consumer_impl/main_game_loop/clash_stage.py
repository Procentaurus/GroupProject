from gameMechanics.scripts.basic_mechanics import get_new_morale
from gameMechanics.queries import get_a_card_serialized

from ....enums import MessageType, PlayerState
from ....models.queries import add_reaction_card_to_owned, remove_reaction_card
from ....messager.scheduler import remove_delayed_task, update_game_user_state
from .common import SurrenderMoveHandler, InitCardsManager
from .abstract import MoveHandler, StageHandler
from .checkers import *


class ClashStageHandler(StageHandler):

    def __init__(self, consumer, message_type, data):
        super().__init__(consumer, message_type, data)

    async def perform_stage(self):
        handler = None
        if self._message_type == MessageType.ACTION_MOVE:
            handler = ActionMoveHandler(self._consumer, self._data)
        elif self._message_type == MessageType.REACTION_MOVE:
            handler = ReactionMoveHandler(self._consumer, self._data)
        elif self._message_type == MessageType.SURRENDER_MOVE:
            handler = SurrenderMoveHandler(self._consumer)
        else:
            e_s = ErrorSender(self._consumer)
            await e_s.send_wrong_message_type_info()
            return

        await handler.perform_move()


class ActionMoveHandler(MoveHandler):

    def __init__(self, consumer, data):
        super().__init__(consumer)
        self._game = consumer.get_game()
        self._a_card = data.get("id")

    async def _verify_move(self):
        if not self._any_card_sent(): return False

        g_v = GameVerifier(self._consumer)
        if not await g_v.verify_next_move_performer(): return False
        if not await g_v.verify_game_next_move_type("action"): return False

        p_v = PlayerVerifier(self._consumer)
        if not await p_v.verify_player_in_clash(): return False

        a_c_c = ActionCardsChecker([self._a_card])
        c_v = CardVerifier(self._consumer, a_c_c)
        if not await c_v.verify_cards_for_clash(): return False
        if not await g_v.verify_turn_update_successful(): return False
        return True

    async def _perform_move_mechanics(self, is_delayed):
        game_user = self._consumer.get_game_user()
        await game_user.remove_action_card(self._a_card)
        await self._consumer.send_message_to_opponent(
            {"action_card" : await get_a_card_serialized(self._a_card)},
            "opponent_move"
        )

        self._consumer.decrease_action_moves()
        if self._consumer.get_action_moves_left() == 0:
            update_game_user_state(
                str(self._game.id),
                str(game_user.id),
                PlayerState.AWAIT_CLASH_END
            )
        if not is_delayed:
            remove_delayed_task(f'limit_action_time_{game_user.id}')
        self._consumer.limit_player_reaction_time()

    def _any_card_sent(self):
        return False if (self._a_card is None or self._a_card == []) else True


class ReactionMoveHandler(MoveHandler):

    def __init__(self, consumer, data):
        super().__init__(consumer)
        self._game = consumer.get_game()
        self._r_cards = data.get("reaction_cards")
        self._g_u = self._consumer.get_game_user()

        # Current user new values
        self._user_r_cards_gained = None
        self._user_a_cards_gained = None
        self._new_user_morale = None
        self._money_user_gained = None

        # Opponent new values
        self._opp_r_cards_gained = None
        self._opp_a_cards_gained = None
        self._new_opp_morale = None
        self._money_opp_gained = None

    async def _verify_move(self):
        g_v = GameVerifier(self._consumer)
        if not await g_v.verify_next_move_performer(): return False
        if not await g_v.verify_game_next_move_type("reaction"): return False

        p_v = PlayerVerifier(self._consumer)
        if not await p_v.verify_player_in_clash_or_wait_for_clash_end():
            return False

        r_c_c = ReactionCardsChecker(self._r_cards)
        c_v = CardVerifier(self._consumer, r_c_c)
        if not await c_v.verify_cards_for_clash(): return False
        if not await g_v.verify_turn_update_successful(): return False
        return True
            
    async def _perform_move_mechanics(self, is_delayed):
        if not is_delayed:
            remove_delayed_task(f'limit_reaction_time_{self._g_u.id}')

        opp = self._consumer.get_opponent()
        await self._consumer.send_message_to_opponent(
            {"reaction_cards" : await self._get_opponent_move_resp_body()},
            "opponent_move")

        await self._process_clash_results(opp)
        await self._add_gains_to_players_accounts()
        await self._remove_all_used_reaction_cards()
        await self._send_clash_result_to_players()
        await self._set_winner_if_exist(opp)

        if self._consumer.is_winner():
            await self._consumer.send_message_to_group(
                {"winner" : self._consumer.get_winner()},
                "game_end")
            return

        self._consumer.decrease_reaction_moves()
        if self._consumer.get_action_moves_left() > 0:
            self._consumer.limit_player_action_time(self._g_u)
            return

        if not opp.wait_for_clash_end(str(self._game.id)):
            e_s = ErrorSender(self._consumer)
            await e_s.send_improper_state_error("reaction_move")
            return

        await self._consumer.send_message_to_opponent({}, "clash_end")
        await self._consumer.clash_end()
        self.set_players_states_in_hub(opp)
        self._consumer.set_action_card_id_played_by_opp(None)

        mng = InitCardsManager(self._consumer)
        await mng.manage_cards()
        if not is_delayed:
            remove_delayed_task(f'limit_reaction_time_{self._g_u.id}')
        self._consumer.limit_players_hub_time()

    def set_players_states_in_hub(self, opp):
        update_game_user_state(
            str(self._game.id),
            str(self._g_u.id),
            PlayerState.IN_HUB
        )
        update_game_user_state(
            str(self._game.id),
            str(opp.id),
            PlayerState.IN_HUB
        )

    async def _get_opponent_move_resp_body(self):
        resp_body = []

        for r_card_data in self._r_cards:
            card_data = {"amount": r_card_data.get("amount")}
            id = r_card_data.get("id")
            card_data["card"] = await get_r_card_serialized(id)
            resp_body.append(card_data)
        return resp_body

    async def _process_clash_results(self, opp):
        a_card = self._consumer.get_action_card_id_played_by_opp()
        (new_opp_morale, opp_money, new_user_morale, user_money) = (
            await get_new_morale(self._g_u, opp, a_card, self._r_cards)
        )
        self._set_money_opp_gained(opp_money)
        self._set_new_opp_morale(new_opp_morale)
        self._set_money_user_gained(user_money)
        self._set_new_user_morale(new_user_morale)

    async def _set_winner_if_exist(self, opp):
        if opp.has_lost():
            self._consumer.set_winner(self._g_u.conflict_side)
        elif self._g_u.has_lost():
            self._consumer.set_winner(opp.conflict_side)

    async def _send_clash_result_to_players(self):
        user_rsp_body = self._get_clash_result_response_body_for_user()
        await self._consumer.clash_result(user_rsp_body)

        opp_rsp_body = self._get_clash_result_response_body_for_opp()
        await self._consumer.send_message_to_opponent(
            opp_rsp_body, "clash_result")

    async def _add_gains_to_players_accounts(self):
        await self._add_all_gains_to_user_account()
        await self._add_all_gains_to_opp_account()

    async def _add_all_gains_to_user_account(self):
        u = self._consumer.get_game_user()
        await u.set_morale(self._new_user_morale)
        await u.add_money(self._money_user_gained)
        await self._add_all_action_cards(u, self._user_a_cards_gained)
        await self._add_all_reaction_cards(u, self._user_r_cards_gained)

    async def _add_all_gains_to_opp_account(self):
        opp = await self._game.get_opponent_player(self._g_u)
        await opp.set_morale(self._new_opp_morale)
        await opp.add_money(self._money_opp_gained)
        await self._add_all_action_cards(opp, self._opp_a_cards_gained)
        await self._add_all_reaction_cards(opp, self._opp_r_cards_gained)

    def _get_clash_result_response_body_for_user(self):
        return {
            "new_player_morale" : self._new_user_morale,
            "new_opponent_morale" : self._new_opp_morale,
            "money_gained" : self._money_user_gained,
            "action_cards_gained" : self._user_a_cards_gained,
            "reaction_cards_gained" : self._user_r_cards_gained
        }

    def _get_clash_result_response_body_for_opp(self):
        return {
            "new_player_morale" : self._new_opp_morale,
            "new_opponent_morale" : self._new_user_morale,
            "money_gained" : self._money_opp_gained,
            "action_cards_gained" : self._opp_a_cards_gained,
            "reaction_cards_gained" : self._opp_r_cards_gained
        }

    async def _remove_all_used_reaction_cards(self):
        if self._any_cards_sent():
            for r_card_data in self._r_cards:
                await remove_reaction_card(
                    self._g_u, r_card_data.get("id"), r_card_data.get("amount"))

    async def _add_all_reaction_cards(self, game_user, r_cards_gained):
        if r_cards_gained is not None:
            for r_card_data in r_cards_gained:
                await add_reaction_card_to_owned(
                    game_user, r_card_data.get("id"), r_card_data.get("amount"))

    async def _add_all_action_cards(self, game_user, a_cards_gained):
        if a_cards_gained is not None:
            for a_card in a_cards_gained:
                await game_user.add_action_card(a_card)

    def _set_user_r_cards_gained(self, value):
        self._user_r_cards_gained = value

    def _set_user_a_cards_gained(self, value):
        self._user_a_cards_gained = value

    def _set_new_user_morale(self, value):
        self._new_user_morale = value

    def _set_money_user_gained(self, value):
        self._money_user_gained = value

    def _set_opp_r_cards_gained(self, value):
        self._opp_r_cards_gained = value

    def _set_opp_a_cards_gained(self, value):
        self._opp_a_cards_gained = value

    def _set_new_opp_morale(self, value):
        self._new_opp_morale = value

    def _set_money_opp_gained(self, value):
        self._money_opp_gained = value

    def _any_cards_sent(self):
        return False if (self._r_cards is None or self._r_cards == []) else True
