import random
from rest_framework import serializers
from channels.db import database_sync_to_async

from gameMechanics.models import ReactionCard, ActionCard

# Import your serializers
from gameMechanics.serializers import ReactionCardDataSerializer, ActionCardDataSerializer

@database_sync_to_async
def get_random_card_ids(model, count, player_type):
    all_instances = model.objects.filter(playerType=player_type)
    random_instances = random.sample(list(all_instances), count)
    
    # Serialize instances using appropriate serializer
    if model == ReactionCard:
        serializer = ReactionCardDataSerializer(random_instances, many=True)
    elif model == ActionCard:
        serializer = ActionCardDataSerializer(random_instances, many=True)
    else:
        raise ValueError("Unsupported model type")
    
    # Retrieve serialized data
    serialized_data = serializer.data
    
    return serialized_data

async def get_initial_shop_for_player(num_reaction_cards, num_action_cards, player_type):
    reaction_card_instances = await get_random_card_ids(ReactionCard, num_reaction_cards, player_type)
    action_card_instances = await get_random_card_ids(ActionCard, num_action_cards, player_type)

    return reaction_card_instances, action_card_instances
