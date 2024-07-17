import random
from rest_framework import serializers
from channels.db import database_sync_to_async

from gameMechanics.models import ReactionCard, ActionCard

# Import your serializers
from gameMechanics.serializers import ReactionCardDataSerializer, ActionCardDataSerializer

@database_sync_to_async
def get_random_card_ids(model, count, player_type):
    print("------------------------------",model)
    print(count)
    print(player_type)
    all_instances = model.objects.filter(playerType=player_type)
    print("all_instances")
    print(all_instances)
    random_instances = random.sample(list(all_instances), count)
    print("random_instances")
    print(random_instances)

    # Serialize instances using appropriate serializer
    if model == ReactionCard:
        serialized_data = []
        # Create a dict list for Reaction Cards
        for random_instance in random_instances:
            serialized_data.append({
                'card': ReactionCardDataSerializer(random_instance).data,
                'amount': random.randint(1, 5)
            })
    elif model == ActionCard:
        # Create Action Card serialized list
        serializer = ActionCardDataSerializer(random_instances, many=True)
        serialized_data = serializer.data
    else:
        raise ValueError("Unsupported model type")    

    return serialized_data

async def get_initial_shop_for_player(num_reaction_cards, num_action_cards, player_type):
    reaction_card_instances = await get_random_card_ids(ReactionCard, num_reaction_cards, player_type)
    action_card_instances = await get_random_card_ids(ActionCard, num_action_cards, player_type)

    return reaction_card_instances, action_card_instances
