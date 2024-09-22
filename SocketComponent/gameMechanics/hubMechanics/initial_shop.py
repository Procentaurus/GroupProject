import random
from channels.db import database_sync_to_async

from gameMechanics.models import ReactionCard, ActionCard

# Import your serializers
from gameMechanics.serializers import ReactionCardDataSerializer, ActionCardDataSerializer

@database_sync_to_async
def get_random_card_ids(model, count, player_type):
    # Filter out the mock cards
    all_instances = model.objects.filter(playerType=player_type).exclude(name__in=["Insult the teacher", "Insult the student"])
    random_instances = random.sample(list(all_instances), count)

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
