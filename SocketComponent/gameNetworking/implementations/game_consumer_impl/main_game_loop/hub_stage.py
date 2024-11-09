from gameNetworking.enums import MessageType

from ....models.queries import *
from ....enums import PlayerState
from ....messager.scheduler import remove_delayed_task
from ....messager.scheduler import check_game_user_state
from ....messager.scheduler import update_game_user_state
from .checkers import *
from .common import SurrenderMoveHandler, ShopCardsAdder, CardSender
from .abstract import MoveHandler, StageHandler


class HubStageHandler(StageHandler):

    def __init__(self, consumer, message_type, data):
        super().__init__(consumer, message_type, data)

    async def perform_stage(self):
        handler = None
        if self._message_type == MessageType.PURCHASE_MOVE:
            handler = PurchaseMoveHandler(self._consumer, self._data)
        elif self._message_type == MessageType.READY_MOVE:
            handler = ReadyMoveHandler(self._consumer)
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

    def __init__(self, consumer):
        super().__init__(consumer)
        self._game = self._consumer.get_game()
        self._g_u = self._consumer.get_game_user()

    async def _verify_move(self):
        p_v = PlayerVerifier(self._consumer)
        if await p_v.verify_player_wait_for_clash(): return False
        if not await p_v.verify_player_in_hub("purchase move"): return False
        self.logger.info(f"User({self._g_u.user_id})'s ready move passed"
                         " verification")
        return True

    async def _perform_move_mechanics(self, is_delayed):
        opp = self._consumer.get_opponent()
        opponent_state = check_game_user_state(str(self._game.id), str(opp.id))
        if opp.is_in_hub(str(self._game.id)):
            update_game_user_state(
                str(self._game.id),
                str(self._g_u.id),
                PlayerState.AWAIT_CLASH_START
            )
        elif opp.wait_for_clash_start(str(self._game.id)):
            await self._send_clash_start_info()
            player_to_move = self.get_next_player_to_move(opp)
            self._consumer.limit_player_action_time(player_to_move)
        else:
            if not is_delayed:
                await self._consumer.critical_error(
                    f"Improper opponent player state: {opponent_state}")
            return

        await self._g_u.remove_all_action_cards_from_shop()
        await remove_all_reaction_cards_from_shop(self._g_u)
        if not is_delayed:
            remove_delayed_task(f'limit_hub_time_{str(self._g_u.id)}')
        self.logger.info(f"User({self._g_u.user_id}) performed ready move")

    async def _send_clash_start_info(self):
        await self._consumer.send_message_to_group(
            {"next_move_player" : self._game.next_move_player},
            "clash_start")

    def get_next_player_to_move(self, opp):
        if self._game.next_move_player == opp.conflict_side: return opp
        else: return  self._g_u


class RerollMoveHandler(MoveHandler):

    def __init__(self, consumer):
        super().__init__(consumer)

    async def _verify_move(self):
        p_v = PlayerVerifier(self._consumer)
        if await p_v.verify_player_wait_for_clash(): return False
        if not await p_v.verify_player_in_hub("reroll move"): return False
        if not await p_v.verify_player_can_reroll(): return False
        self.logger.info(f"User({self._consumer.get_game_user().user_id})'s"
                    " reroll move passed verification")
        return True

    async def _perform_move_mechanics(self, is_delayed):
        g_u = self._consumer.get_game_user()
        await g_u.buy_reroll()
        await g_u.increase_reroll_price()

        (new_a_cards, new_r_cards) = await get_shop_for_player(2, 5, g_u.player_type)

        s_c_a = ShopCardsAdder(g_u, new_a_cards, new_r_cards)
        await s_c_a.add_all_cards_shop()
 
        await g_u.remove_all_action_cards_from_shop()
        await remove_all_reaction_cards_from_shop(g_u)

        c_s = CardSender(self._consumer, new_a_cards, new_r_cards)
        await c_s.send_cards_to_player()
        await self._consumer.send_json({
            'type' : "reroll_confirmation",
            'new_reroll_price' : g_u.get_reroll_price()
        })
        self.logger.info(f"User({self._consumer.get_game_user().user_id})"
                         " performed reroll move")


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

        self.logger.info(f"User({self._consumer.get_game_user().user_id})'s"
            " purchase move passed verification")
        return True
    
    async def _perform_move_mechanics(self, is_delayed):
        g_u = self._consumer.get_game_user()

        if self._any_action_cards_sent():
            for a_card_id in self._a_cards:
                await self._purchase_action_card(a_card_id)

        if self._any_reaction_cards_sent():
            for r_card_data in self._r_cards:
                id = r_card_data.get("id")
                amount = r_card_data.get("amount")
                await self._purchase_reaction_card(id, amount)
            
        await self._consumer.purchase_result({"new_money_amount" : g_u.money})
        self.logger.info(f"User({self._consumer.get_game_user().user_id})"
                         " performed purchase move")
        
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
