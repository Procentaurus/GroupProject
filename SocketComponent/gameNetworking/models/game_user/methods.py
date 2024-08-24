from channels.db import database_sync_to_async

from gameMechanics.queries import get_a_card_sync

@database_sync_to_async
def check_action_card_owned(self, a_card_id):
    try:
        self.owned_action_cards.get(id=a_card_id)
        return True
    except Exception as e:
        return False

@database_sync_to_async
def add_action_card(self, a_card_id):
    action_card = get_a_card_sync(a_card_id)
    self.owned_action_cards.add(action_card)
    self.save()

@database_sync_to_async
def remove_action_card(self, a_card_id):
    action_card = self.owned_action_cards.get(id=a_card_id)
    self.owned_action_cards.remove(action_card)
    self.save()

@database_sync_to_async
def check_action_card_in_shop(self, a_card_id):
    try:
        self.action_cards_in_shop.get(id=a_card_id)
        return True
    except Exception as e:
        return False

@database_sync_to_async
def remove_action_card_from_shop(self, a_card_id):
    action_card = self.action_cards_in_shop.get(id=a_card_id)
    self.action_cards_in_shop.remove(action_card)
    self.save()

@database_sync_to_async
def add_action_card_to_shop(self, a_card_id):
    action_card = get_a_card_sync(a_card_id)
    self.action_cards_in_shop.add(action_card)
    self.save()

@database_sync_to_async
def remove_all_action_cards_from_shop(self):
    action_cards_in_shop = self.action_cards_in_shop.all()
    for action_card in action_cards_in_shop:
        self.action_cards_in_shop.remove(action_card)
    self.save()

@database_sync_to_async
def backup(self, consumer):
    self.action_moves_left = consumer.get_action_moves_left()
    self.reaction_moves_left = consumer.get_reaction_moves_left()
    played_a_card = consumer.get_action_card_id_played_by_opp()
    if played_a_card is not None:
        self.opp_played_action_card_id = played_a_card
    self.save()
    consumer.logger.info(f"User({self.user_id})'s data has been backuped")

async def buy_reroll(self):
    await self.subtract_money(self.reroll_price)
