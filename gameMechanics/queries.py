from channels.db import database_sync_to_async
from django.core.exceptions import ValidationError

from .models import ActionCard, ReactionCard
from .serializers import ActionCardDataSerializer, ReactionCardDataSerializer


########### Action card ###########

@database_sync_to_async
def get_a_card(id):
    try:
        card = ActionCard.objects.get(id=id)
        return card
    except ActionCard.DoesNotExist:
        return None
    
def get_a_card_sync(id):
    try:
        card = ActionCard.objects.get(id=id)
        return card
    except ActionCard.DoesNotExist:
        return None

@database_sync_to_async
def get_a_card_serialized(id):
    try:
        card = ActionCard.objects.get(id=id)
        serializer = ActionCardDataSerializer(card)
        return serializer.data
    except ActionCard.DoesNotExist:
        return {}

@database_sync_to_async
def check_action_card_exist(id):
    try:
        _ = ActionCard.objects.get(id=id)
        return True
    except (ActionCard.DoesNotExist, ValidationError):
        return False            


########### Reaction card ###########

@database_sync_to_async
def check_reaction_card_exist(id):
    try:
        _ = ReactionCard.objects.get(id=id)
        return True
    except ReactionCard.DoesNotExist:
        return False
    
@database_sync_to_async
def get_r_card(id):
    try:
        card = ReactionCard.objects.get(id=id)
        return card
    except ReactionCard.DoesNotExist:
        return None

def get_r_card_sync(id):
    try:
        card = ReactionCard.objects.get(id=id)
        return card
    except ReactionCard.DoesNotExist:
        return None
    
@database_sync_to_async
def get_r_card_serialized(id):
    try:
        card = ReactionCard.objects.get(id=id)
        serializer = ReactionCardDataSerializer(card)
        return serializer.data
    except ReactionCard.DoesNotExist:
        return {}
