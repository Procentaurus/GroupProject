from gameMechanics.models import ActionCard

from ..common import decrease_card_amount


### owned action card ###

def check_action_card_owned_impl(game_user, a_card_id):
    try:
        game_user.owned_action_cards.get(id=a_card_id)
        return True
    except Exception as e:
        return False
    
def add_action_card_impl(game_user, a_card_id):
    action_card = ActionCard.objects.get(id=a_card_id)
    game_user.owned_action_cards.add(action_card)
    game_user.save()

def remove_action_card_impl(game_user, a_card_id):
    action_card = game_user.owned_action_cards.get(id=a_card_id)
    game_user.owned_action_cards.remove(action_card)
    game_user.save()


### action card in shop ###

def check_action_card_in_shop_impl(game_user, a_card_id):
    try:
        game_user.action_cards_in_shop.get(id=a_card_id)
        return True
    except Exception as e:
        return False

def remove_action_card_from_shop_impl(game_user, a_card_id):
    action_card = game_user.action_cards_in_shop.get(id=a_card_id)
    game_user.action_cards_in_shop.remove(action_card)
    game_user.save()

def add_action_card_to_shop_impl(game_user, a_card_id):
    action_card = ActionCard.objects.get(id=a_card_id)
    game_user.action_cards_in_shop.add(action_card)
    game_user.save()


### owned reaction card ###

def check_reaction_card_owned_impl(game_user, r_card_id, amount):  
    owned_card = game_user.owned_reaction_cards.filter(
        reaction_card__id=r_card_id).first()
    
    if owned_card is not None:
        return True if owned_card.amount >= amount else False
    else: return False

def remove_reaction_card_impl(game_user, r_card_id, amount):
    owned_card = game_user.owned_reaction_cards.filter(
        reaction_card__id=r_card_id).first()

    if owned_card is not None:
        decrease_card_amount(owned_card, amount)


### reaction card in shop ###
    
def check_reaction_card_in_shop_impl(game_user, r_card_id, amount):
    card_in_shop = game_user.reaction_cards_in_shop.filter(
        reaction_card__id=r_card_id).first()
    
    if card_in_shop is not None:
        return True if card_in_shop.amount >= amount else False
    else:
        return False
    
def remove_reaction_card_from_shop_impl(game_user, r_card_id, amount):
    card_in_shop = game_user.reaction_cards_in_shop.filter(
        reaction_card__id=r_card_id).first()

    if card_in_shop is not None:
        decrease_card_amount(card_in_shop, amount)
