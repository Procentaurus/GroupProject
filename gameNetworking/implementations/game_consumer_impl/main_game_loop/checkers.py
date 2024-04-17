from gameMechanics.queries import *

from ....models.queries import *
from .common import *


class CardVerifier:
    def __init__(self, consumer, card_checker):
        self._consumer = consumer
        self._c_c = card_checker

    async def _verify_cards_data_structure(self):
        if not self._c_c.is_cards_data_structure_valid():
            e_s = ErrorSender(self._consumer)
            await e_s.send_invalid_data_structure_info()
            return False
        return True

    async def _verify_cards_exist(self):
        not_existing_cards = await self._c_c.check_cards_exist()
        if not_existing_cards != []:
            e_s = ErrorSender(self._consumer)
            await e_s.send_cards_not_exist_info(not_existing_cards)
            return False
        return True
    
    async def _verify_cards_in_shop(self):
        g_u = self._consumer.get_game_user()
        cards_not_in_shop = await self._c_c.check_cards_in_shop(g_u)
        if cards_not_in_shop != []:
            e_s = ErrorSender(self._consumer)
            await e_s.send_cards_not_in_shop_info(cards_not_in_shop)
            return False
        return True

    async def _verify_cards_owned(self):
        g_u = self._consumer.get_game_user()
        cards_not_owned = await self._c_c.check_cards_owned(g_u)
        if cards_not_owned != []:
            e_s = ErrorSender(self._consumer)
            await e_s.send_card_not_owned_info(cards_not_owned)
            return False
        return True
    
    async def verify_cards_for_purchase(self):
        if not self._c_c.is_cards_data_empty():
            if await self._verify_cards_data_structure():
                if await self._verify_cards_exist():
                    return await self._verify_cards_in_shop()
            return False
        return True
    
    async def verify_cards_for_clash(self):
        if not self._c_c.is_cards_data_empty():
            if await self._verify_cards_data_structure():
                if await self._verify_cards_exist():
                    return await self._verify_cards_owned()
            return False
        return True


class CardChecker:

    def __init__(self, cards_data):
        self._cards_data = cards_data if cards_data is not None else []

    def is_cards_data_empty(self):
        if self._cards_data == []:
            return True
        else:
            return False


class ActionCardsChecker(CardChecker):

    def __init__(self, cards_data):
        super().__init__(cards_data)

    def is_cards_data_structure_valid(self):
        if isinstance(self._cards_data, list):
            return all(isinstance(item, str) for item in self._cards_data)
        return False

    async def check_cards_exist(self):
        not_existing_cards = []

        for card_id in self._cards_data:
            card_exist = await check_action_card_exist(card_id)
            if not card_exist:
                not_existing_cards.append(card_id)

        return not_existing_cards
    
    async def check_cards_in_shop(self, game_user):
        cards_not_in_shop = []

        for card_id in self._cards_data:
            action_card_in_shop = await game_user.check_action_card_in_shop(
                card_id)
            if not action_card_in_shop:
                cards_not_in_shop.append(card_id)

        return cards_not_in_shop
    
    async def check_cards_owned(self, game_user):
        cards_not_owned = []

        for card_id in self._cards_data:
            if not await game_user.check_action_card_owned(card_id):
                cards_not_owned.append(card_id)
        
        return cards_not_owned


class ReactionCardsChecker(CardChecker):

    def __init__(self, cards_data):
        super().__init__(cards_data)

    def is_cards_data_structure_valid(self):
        return (
                isinstance(self._cards_data, list) and 
                all(
                    isinstance(item, dict) and 
                    "id" in item and 
                    "amount" in item 
                    for item in self._cards_data
                )
            )

    async def check_cards_exist(self):
        not_existing_cards = []

        for card_data in self._cards_data:
            id = card_data.get("id")
            card_exist = await check_reaction_card_exist(id)
            if not card_exist:
                not_existing_cards.append(id)

        return not_existing_cards
    
    async def check_cards_in_shop(self, game_user):
        cards_not_in_shop = []

        for card_data in self._cards_data:
            id = card_data.get("id")
            amount = card_data.get("amount")
            card_in_shop = await check_reaction_card_in_shop(
                game_user, id, amount)
            if not card_in_shop:
                cards_not_in_shop.append([id, amount])

        return cards_not_in_shop
    
    async def check_cards_owned(self, game_user):
        cards_not_owned = []

        for card_data in self._cards_data:
            id = card_data.get("id")
            amount = card_data.get("amount")
            if not await check_reaction_card_owned(game_user, id, amount):
                cards_not_owned.append([id, amount])
        
        return cards_not_owned


class CardCostVerifier:

    """
    Class'es functions dont perform any validation, so before using it
    existence of all cards must be confirmed    
    """

    def __init__(self, consumer, a_cards_data, r_cards_data):
        self._consumer = consumer
        self._a_cards_data = a_cards_data if a_cards_data is not None else []
        self._r_cards_data = r_cards_data if r_cards_data is not None else []

    async def _count_r_cards_cost(self):
        cards_total_price = 0

        for card_data in self._r_cards_data:
            id = card_data.get("id")
            card = await get_r_card(id)
            cards_total_price += card.price

        return cards_total_price
    
    async def _count_a_cards_cost(self):
        cards_total_price = 0

        for card_id in self._a_cards_data:
            action_card = await get_a_card(card_id)
            cards_total_price += action_card.price

        return cards_total_price
    
    async def _can_player_afford_cards(self):
        player_money = self._consumer.get_game_user().money
        a_cards_cost = await self._count_a_cards_cost()
        r_cards_cost = await self._count_r_cards_cost()

        if player_money >= a_cards_cost + r_cards_cost:
            return True
        return False
    
    async def verify_player_can_afford_cards(self):   
        if not await self._can_player_afford_cards():
            e_s = ErrorSender(self._consumer)
            await e_s.send_not_enough_money_info()
            return False
        return True


class PlayerVerifier:

    def __init__(self, consumer, player=None):
        self._consumer = consumer
        self._player = consumer.get_game_user() if player is None else player

    async def verify_player_wait_for_clash(self):
        if self._player.wait_for_clash_start():
            e_s = ErrorSender(self._consumer)
            await e_s.send_improper_move_info("readyness already declared")
            return True
        return False
    
    async def verify_player_in_hub(self, move):
        if not self._player.is_in_hub():
            e_s = ErrorSender(self._consumer)
            await e_s.send_improper_state_error(move)
            return False
        return True
    
    async def verify_player_in_clash(self):
        if not self._player.is_in_clash():
            e_s = ErrorSender(self._consumer)
            await e_s.send_improper_state_error("action_move")
            return False
        return True
    
    async def verify_player_in_clash_or_wait_for_clash_end(self):
        p = self._player
        if not p.is_in_clash() and not p.wait_for_clash_end():
            e_s = ErrorSender(self._consumer)
            await e_s.send_improper_state_error("reaction_move")
            return False
        return True
    
    async def verify_player_can_reroll(self):
        if not self._player.can_afford_reroll():
            e_s = ErrorSender(self._consumer)
            await e_s.send_improper_move_info("not enough money to reroll")
            return False
        return True


class GameVerifier:

    def __init__(self, consumer, game):
        self._consumer = consumer
        self._game = game
    
    async def verify_game_exist(self):
        g = await get_game(self._consumer.get_game_id())
        if g is None:
            game_user = self._consumer.get_game_user()
            e_s = ErrorSender(self._consumer)
            await e_s.send_game_not_started_info(game_user.conflict_side)
            return False
        return True

    async def verify_game_next_move_type(self, proper_move):
        if self._game.next_move_type != proper_move:
            e_s = ErrorSender(self._consumer)
            await e_s.send_improper_move_info("wrong move type")
            return False
        return True
        
    async def verify_turn_update_successful(self):
        if not await self._game.update_after_turn():
            e_s = ErrorSender(self._consumer)
            await e_s.send_turn_update_fail_error()
            return False
        return True
    
    async def verify_next_move_performer(self):
        game_user = self._consumer.get_game_user()
        if self._game.next_move_player != game_user.conflict_side:
            e_s = ErrorSender(self._consumer)
            await e_s.send_improper_move_info("not your turn")
            return False
        return True
