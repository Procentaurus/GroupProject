from channels.db import database_sync_to_async

from .models import ActionCard, ReactionCard


@database_sync_to_async
def get_action_cards(given_task, choice, number_of_cards_to_return):
    pass


@database_sync_to_async
def get_reaction_cards(given_task, choice, number_of_cards_to_return):
    pass


@database_sync_to_async
def calculate_change_in_morale(action_card, reaction_cards):
    pass


########### Action card ###########

@database_sync_to_async
def get_action_card(action_card_id):
    try:
        card = ActionCard.objects.get(action_card_id)
        return card
    except ActionCard.DoesNotExist:
        return None  

@database_sync_to_async
def check_action_card_exist(action_card_id):
    try:
        _ = ActionCard.objects.get(action_card_id)
        return True
    except ActionCard.DoesNotExist:
        return False            


########### Reaction card ###########

@database_sync_to_async
def check_reaction_card_exist(reaction_card_id):
    try:
        _ = ReactionCard.objects.get(reaction_card_id)
        return True
    except ReactionCard.DoesNotExist:
        return False
    
@database_sync_to_async
def get_reaction_card(reaction_card_id):
    try:
        card = ReactionCard.objects.get(reaction_card_id)
        return card
    except ReactionCard.DoesNotExist:
        return None  