from channels.db import database_sync_to_async
from gameMechanics.models import *


@database_sync_to_async
def check_if_own_action_card_impl(game_user, action_card_id):
    try:
        game_user.action_cards.get(id=action_card_id)
        return True
    except ActionCard.DoesNotExist:
        return False

@database_sync_to_async
def remove_action_card_impl(game_user, action_card_id):
    try:
        action_card = ActionCard.objects.get(uuid=action_card_id)
        game_user.action_cards.remove(action_card)
        game_user.save()
        return True
    except ActionCard.DoesNotExist:
        return False
    
@database_sync_to_async
def add_action_card_impl(game_user, action_card_id):
    try:
        action_card = ActionCard.objects.get(uuid=action_card_id)
        game_user.action_cards.add(action_card)
        game_user.save()
        return True
    except ActionCard.DoesNotExist:
        return False
    
@database_sync_to_async
def check_if_own_reaction_card_impl(game_user, reaction_card_id, amount=1):

    is_owning_card = game_user.reaction_cards.filter(
        reaction_card__id=reaction_card_id,
        amount__gte=amount
    ).exists()

    return is_owning_card

@database_sync_to_async
def remove_reaction_card_impl(game_user, reaction_card_id, amount=1):

    reaction_card, owned_card = None, None

    try:
        reaction_card = ReactionCard.objects.get(id=reaction_card_id)
    except ReactionCard.DoesNotExist:
        return "ReactionCard.DoesNotExist"
    
    try:
        owned_card = OwnedReactionCard.objects.get(
            gameUser=game_user,
            reaction_card=reaction_card,
        )
    except OwnedReactionCard.DoesNotExist:
        return "OwnedReactionCard.DoesNotExist"
    
    if owned_card.amount > amount:
        owned_card.amount -= amount
        owned_card.save()
        return True
    else:
        return "Not enough cards."
    
@database_sync_to_async
def add_reaction_card_impl(game_user, reaction_card_id, amount=1):
    try:
        reaction_card = ReactionCard.objects.get(id=reaction_card_id)

        # Retrieve the OwnedReactionCard instance or create a new one if it doesn't exist
        owned_card, _ = OwnedReactionCard.objects.get_or_create(
            gameUser=game_user,
            reaction_card=reaction_card,
        )

        # Increment the amount
        owned_card.amount += amount
        owned_card.save()
        return True
    
    except ReactionCard.DoesNotExist:
        return False