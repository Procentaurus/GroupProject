from gameMechanics.scripts.basic_mechanics import get_rerolled_cards

from gameNetworking.enums import PlayerState, MessageType

from ....models.queries import *
from .checkers import *
from .common import SurrenderMoveHandler, ShopCardsAdder, CardSender
from .abstract import MoveHandler, StageHandler


class HubStageHandler(StageHandler):

    def __init__(self, consumer, game, message_type, data):
        super().__init__(consumer, game, message_type, data)

    async def perform_stage(self):
        handler = None
        if self._message_type == MessageType.PURCHASE_MOVE:
            handler = PurchaseMoveHandler(self._consumer, self._data)
        elif self._message_type == MessageType.READY_MOVE:
            handler = ReadyMoveHandler(self._consumer, self._game)
        elif self._message_type == MessageType.SURRENDER_MOVE:
            handler = SurrenderMoveHandler(self._consumer)
        elif self._message_type == MessageType.REROLL_MOVE:
            handler = RerollMoveHandler(self._consumer)
        else:
            e_s = ErrorSender(self._consumer)
            await e_s.send_wrong_message_type_info()
            return

        await handler.perform_move()


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
        if opponent.is_in_hub():
            await self._player.set_state(PlayerState.AWAIT_CLASH_START)
        elif opponent.wait_for_clash_start():
            await self._send_clash_start_info()
        else:
            await self._consumer.critical_error(
                f"Improper opponent player state: {opponent.state}")

    async def _send_clash_start_info(self):
        await self._consumer.send_message_to_group(
            {"next_move_player" : self._game.next_move_player},
            "clash_start")


class RerollMoveHandler(MoveHandler):

    def __init__(self, consumer):
        super().__init__(consumer)

    async def _verify_move(self):
        p_v = PlayerVerifier(self._consumer)
        if await p_v.verify_player_wait_for_clash(): return False
        if not await p_v.verify_player_in_hub("reroll move"): return False
        if not await p_v.verify_player_can_reroll(): return False
        return True

    async def _perform_move_mechanics(self):
        g_u = self._consumer.get_game_user()
        await g_u.subtract_available_rerolls()

        (new_a_cards, new_r_cards) = await get_rerolled_cards(g_u)

        s_c_a = ShopCardsAdder(g_u, new_a_cards, new_r_cards)
        await s_c_a.add_all_cards_shop()
 
        await g_u.remove_all_action_cards_from_shop()
        await remove_all_reaction_cards_from_shop(g_u)

        c_s = CardSender(self._consumer, new_a_cards, new_r_cards)
        c_s.send_cards_to_player()


class PurchaseMoveHandler(MoveHandler):

    def __init__(self, consumer, data):
        super().__init__(consumer)
        self._a_cards = data.get("action_cards")
        self._r_cards = data.get("reaction_cards")

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
    
    async def _perform_move_mechanics(self):
        g_u = self._consumer.get_game_user()

        if self._any_action_cards_sent():
            for a_card_id in self._a_cards:
                await self._purchase_action_card(a_card_id)

        if self._any_reaction_cards_sent():
            for r_card_data in self._r_cards:
                id = r_card_data.get("id")
                amount = r_card_data.get("amount")
                await self._purchase_reaction_card(id, amount)
            
        await self._consumer.purchase_result(
            {"new_money_amount" : g_u.money})
        
    def _any_action_cards_sent(self):
        return False if (self._a_cards is None or self._a_cards == []) else True
    
    def _any_reaction_cards_sent(self):
        return False if (self._r_cards is None or self._r_cards == []) else True

    async def _purchase_action_card(self, card_id):
        card_price = (await get_a_card(card_id)).price
        g_u = self._consumer.get_game_user()

        await g_u.add_action_card(card_id)
        await g_u.subtract_money(card_price)
        await g_u.remove_action_card_from_shop(card_id)

    async def _purchase_reaction_card(self, card_id, amount):

        reaction_card_price = (await get_r_card(card_id)).price
        g_u = self._consumer.get_game_user()

        await add_reaction_card_to_owned(g_u, card_id, amount)
        await g_u.subtract_money(reaction_card_price * amount)
        await remove_reaction_card_from_shop(g_u, card_id, amount)
