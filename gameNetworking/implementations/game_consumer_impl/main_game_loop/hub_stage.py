from gameNetworking.enums import PlayerState, MessageType
from .checkers import *
from .purchasing_cards import purchase_action_card, purchase_reaction_card
from .common import SurrenderMoveHandler
from .abstract import MoveHandler, StageHandler


class HubStageHandler(StageHandler):

    def __init__(self, consumer, game, message_type, data):
        super().__init__(consumer, game, message_type, data)

    async def perform_stage(self):
        if self._message_type == MessageType.PURCHASE_MOVE:
            p_m_h = PurchaseMoveHandler(self._consumer, self._data)
            await p_m_h.perform_move()
        elif self._message_type == MessageType.READY_MOVE:
            r_m_h = ReadyMoveHandler(self._consumer, self._game)
            await r_m_h.perform_move()
        elif self._message_type == MessageType.SURRENDER_MOVE:
            s_m_h = SurrenderMoveHandler(self._consumer)
            await s_m_h.perform_move()
        else:
            e_s = ErrorSender(self._consumer)
            await e_s.send_wrong_message_type_info()


class ReadyMoveHandler(MoveHandler):

    def __init__(self, consumer, game):
        super().__init__(consumer)
        self._game = game
        self._player = self._consumer.get_game_user()

    async def _verify_move(self):
        p_v = PlayerVerifier(self._consumer)
        if await p_v.verify_player_wait_for_clash(): return False
        if not await p_v.verify_player_in_hub("purchase move"): return False
        
        return True

    async def _perform_move_mechanics(self):
        opponent = await self._game.get_opponent_player(self._player)
        if await opponent.is_in_hub():
            await self._player.set_state(PlayerState.AWAIT_CLASH_START)
        elif await opponent.wait_for_clash_start():
            await self._send_clash_start_info()
        else:
            await self._consumer.critical_error(
                f"Improper opponent player state: {opponent.state}")
            
    async def _send_invalid_move_info(self):
        await self._consumer.error("You have already declared readyness.",
            f"{self._player.conflict_side} player tried to declare"
            +" readyness for the clash afresh.")

    async def _send_clash_start_info(self):
        await self._consumer.send_message_to_group(
            {"next_move_player" : self._game.next_move_player},
            "clash_start")


class PurchaseMoveHandler(MoveHandler):

    def __init__(self, consumer, data):
        super().__init__(consumer)
        self._a_cards = data.get("action_cards")
        self._r_cards = data.get("reaction_cards")

    async def _perform_move_mechanics(self):
        g_u = self._consumer.get_game_user()
        for a_card_id in self._a_cards:
            await purchase_action_card(self._consumer, a_card_id)
            await g_u.remove_action_card_from_shop(a_card_id)

        for r_card_data in self._r_cards:
            id = r_card_data.get("reaction_card_id")
            amount = r_card_data.get("amount")
            await purchase_reaction_card(self._consumer, id, amount)
            await g_u.remove_reaction_card_from_shop(id, amount)
            
        await self._consumer.purchase_result(
            {"new_money_amount" : self._consumer.get_game_user().money})

    async def _verify_move(self):
        p_v = PlayerVerifier(self._consumer)
        if await p_v.verify_player_wait_for_clash(): return False
        if not await p_v.verify_player_in_hub("purchase move"): return False

        a_c_c = ActionCardsChecker(self._a_cards)
        a_c_v = CardVerifier(self._consumer, a_c_c)
        if not await a_c_v.verify_cards_for_purchase(): return False

        r_c_c = ReactionCardsChecker(self._r_cards)
        r_c_v = CardVerifier(self._consumer, r_c_c)
        if not await r_c_v.verify_cards_for_purchase(): return False

        c_c_v = CardCostVerifier(self._consumer, self._a_cards, self._r_cards)
        if not await c_c_v.verify_player_can_afford_cards(): return False

        return True
