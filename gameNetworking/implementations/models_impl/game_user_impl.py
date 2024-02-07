from channels.db import database_sync_to_async
from gameMechanics.models import *
from gameNetworking.models import OwnedReactionCard, ReactionCardInShop


@database_sync_to_async
def check_if_own_action_card_impl(game_user, action_card_id):
    try:
        game_user.owned_action_cards.get(id=action_card_id)
        return True
    except ActionCard.DoesNotExist:
        return False
    
@database_sync_to_async
def check_if_have_action_card_in_shop_impl(game_user, action_card_id):
    try:
        game_user.action_cards_in_shop.get(id=action_card_id)
        return True
    except ActionCard.DoesNotExist:
        return False

@database_sync_to_async
def remove_action_card_impl(game_user, action_card_id):
    try:
        action_card = game_user.owned_action_cards.get(id=action_card_id)
        game_user.owned_action_cards.remove(action_card)
        game_user.save()
        return True
    except ActionCard.DoesNotExist:
        return False
    
@database_sync_to_async
def remove_action_card_from_shop_impl(game_user, action_card_id):
    try:
        action_card = game_user.action_cards_in_shop.get(id=action_card_id)
        game_user.action_cards_in_shop.remove(action_card)
        game_user.save()
        return True
    except ActionCard.DoesNotExist:
        return False
    
@database_sync_to_async
def add_action_card_impl(game_user, action_card_id):
    try:
        action_card = ActionCard.objects.get(uuid=action_card_id)
        game_user.owned_action_cards.add(action_card)
        game_user.save()
        return True
    except ActionCard.DoesNotExist:
        return False
    
@database_sync_to_async
def add_action_card_to_shop_impl(game_user, action_card_id):
    try:
        action_card = ActionCard.objects.get(uuid=action_card_id)
        game_user.action_cards_in_shop.add(action_card)
        game_user.save()
        return True
    except ActionCard.DoesNotExist:
        return False

# Before usage check if reaction card of passed id exists
@database_sync_to_async
def check_if_own_reaction_card_impl(game_user, reaction_card_id, amount):  
    try:
        owned_card = OwnedReactionCard.objects.get(
            game_user=game_user,
            reaction_card=ReactionCard.objects.get(id=reaction_card_id),
        )
        return True if owned_card.amount >= amount else False
    
    except OwnedReactionCard.DoesNotExist:
        return False

# Before usage check if reaction card of passed id exists
@database_sync_to_async
def check_if_have_reaction_card_in_shop_impl(game_user, reaction_card_id, amount):   
    try:
        card_in_shop = ReactionCardInShop.objects.get(
            game_user=game_user,
            reaction_card=ReactionCard.objects.get(id=reaction_card_id),
        )
        return True if card_in_shop.amount >= amount else False
    
    except OwnedReactionCard.DoesNotExist:
        return False

# Before usage check if reaction card of passed id exists
@database_sync_to_async
def remove_reaction_card_impl(game_user, reaction_card_id, amount):

    owned_card = None
    reaction_card = ReactionCard.objects.get(id=reaction_card_id)
    try:
        owned_card = OwnedReactionCard.objects.get(
            game_user=game_user,
            reaction_card=reaction_card,
        )
    except OwnedReactionCard.DoesNotExist:
        return False

    result = decrease_card_amount(owned_card, amount)
    return result
    
# Before usage check if reaction card of passed id exists
@database_sync_to_async
def remove_reaction_card_from_shop_impl(game_user, reaction_card_id, amount):

    card_in_shop = None
    reaction_card = ReactionCard.objects.get(id=reaction_card_id)
    try:
        card_in_shop = ReactionCardInShop.objects.get(
            game_user=game_user,
            reaction_card=reaction_card,
        )
    except OwnedReactionCard.DoesNotExist:
        return False

    result = decrease_card_amount(card_in_shop, amount)
    return result
       
# Before usage check if reaction card of passed id exists 
@database_sync_to_async
def add_reaction_card_impl(game_user, reaction_card_id, amount):
    reaction_card = ReactionCard.objects.get(id=reaction_card_id)

    # Retrieve the OwnedReactionCard instance or create a new one if it doesn't exist
    owned_card, had_card_earlier = OwnedReactionCard.objects.get_or_create(
        game_user=game_user,
        reaction_card=reaction_card,
    )

    increase_card_amount(had_card_earlier, owned_card, amount)
    
# Before usage check if reaction card of passed id exists 
@database_sync_to_async
def add_reaction_card_to_shop_impl(game_user, reaction_card_id, amount):
    reaction_card = ReactionCard.objects.get(id=reaction_card_id)

    # Retrieve the OwnedReactionCard instance or create a new one if it doesn't exist
    card_in_shop, had_card_earlier = ReactionCardInShop.objects.get_or_create(
        game_user=game_user,
        reaction_card=reaction_card,
    )

    increase_card_amount(had_card_earlier, card_in_shop, amount)
    
@database_sync_to_async
def increase_card_amount(had_card_earlier, card, amount):
    if had_card_earlier:
        # Increment the amount
        card.amount += amount
        card.save()
        return True
    else:
        card.amount == amount
        card.save()
        return True
    
@database_sync_to_async
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
    