from django.apps import apps

from gameMechanics.models import *


def check_if_own_action_card_impl(game_user, action_card_id):
    try:
        game_user.owned_action_cards.get(id=action_card_id)
        return True
    except Exception as e:
        return False

def check_if_have_action_card_in_shop_impl(game_user, action_card_id):
    try:
        game_user.action_cards_in_shop.get(id=action_card_id)
        return True
    except Exception as e:
        return False

def remove_action_card_impl(game_user, action_card_id):
    try:
        action_card = game_user.owned_action_cards.get(id=action_card_id)
        game_user.owned_action_cards.remove(action_card)
        game_user.save()
        return True
    except Exception as e:
        return False

def remove_action_card_from_shop_impl(game_user, action_card_id):
    try:
        action_card = game_user.action_cards_in_shop.get(id=action_card_id)
        game_user.action_cards_in_shop.remove(action_card)
        game_user.save()
        return True
    except Exception as e:
        return False

def add_action_card_impl(game_user, action_card_id):
    try:
        action_card = ActionCard.objects.get(id=action_card_id)
        game_user.owned_action_cards.add(action_card)
        game_user.save()
        return True
    except Exception as e:
        return False

def add_action_card_to_shop_impl(game_user, action_card_id):
    try:
        action_card = ActionCard.objects.get(id=action_card_id)
        game_user.action_cards_in_shop.add(action_card)
        game_user.save()
        return True
    except Exception as e:
        return False

# Before usage check if reaction card of passed id exists
def check_if_own_reaction_card_impl(game_user, reaction_card_id, amount):  
    owned_card = game_user.owned_reaction_cards.filter(
        reaction_card__id=reaction_card_id).first()
    if owned_card is not None:
        return True if owned_card.amount >= amount else False
    else: return False
    
# Before usage check if reaction card of passed id exists
def check_if_have_reaction_card_in_shop_impl(
    game_user, reaction_card_id, amount):
    
    card_in_shop = game_user.reaction_cards_in_shop.filter(
        reaction_card__id=reaction_card_id).first()
    
    if card_in_shop is not None:
            return True if card_in_shop.amount >= amount else False
    else:
        return False
    
# Before usage check if reaction card of passed id exists
def remove_reaction_card_impl(game_user, reaction_card_id, amount):
    owned_card = game_user.owned_reaction_cards.filter(
        reaction_card__id=reaction_card_id).first()

    if owned_card is not None:
        result = decrease_card_amount(owned_card, amount)
        return result
    else:
        return False
       
# Before usage check if reaction card of passed id exists
def remove_reaction_card_from_shop_impl(game_user, reaction_card_id, amount):
    card_in_shop = game_user.reaction_cards_in_shop.filter(
        reaction_card__id=reaction_card_id).first()

    if card_in_shop is not None:
        result = decrease_card_amount(card_in_shop, amount)
        return result
    else:
        return False

# Before usage check if reaction card of passed id exists 
def add_reaction_card_impl(game_user, reaction_card_id, amount):
    owned_reaction_card_model = apps.get_model(
        'gameNetworking', 'OwnedReactionCard')
    r_card = ReactionCard.objects.get(id=reaction_card_id)

    # Retrieve the OwnedReactionCard instance or create a new one if it doesn't exist
    owned_card, had_card_earlier = owned_reaction_card_model.objects.get_or_create(
        game_user=game_user,
        reaction_card=r_card,
    )

    increase_card_amount(had_card_earlier, owned_card, amount)
    
# Before usage check if reaction card of passed id exists 
def add_reaction_card_to_shop_impl(game_user, reaction_card_id, amount):  
    reaction_card_in_shop_model = apps.get_model(
        'gameNetworking', 'ReactionCardInShop')
    r_card = ReactionCard.objects.get(id=reaction_card_id)
    
    # Retrieve the OwnedReactionCard instance or create a new one if it doesn't exist
    card_in_shop, had_card_earlier = reaction_card_in_shop_model.objects.get_or_create(
        game_user=game_user,
        reaction_card__id=r_card,
    )

    increase_card_amount(had_card_earlier, card_in_shop, amount)
    
def increase_card_amount(had_card_earlier, card, amount):
    if had_card_earlier:
        card.amount += amount
        card.save()
        return True
    else:
        card.amount == amount
        card.save()
        return True
    
def decrease_card_amount(card, amount):
    if card.amount > amount:
        card.amount -= amount
        card.save()
        return True
    elif card.amount == amount:
        card.delete()
        return True
    else:
        return False
