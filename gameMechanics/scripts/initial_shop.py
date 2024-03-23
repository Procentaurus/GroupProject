from gameMechanics.models import ActionCard, ReactionCard
import random
from channels.db import database_sync_to_async

@database_sync_to_async
def get_random_card_ids(model, count, player_type):
    all_instances = model.objects.filter(playerType=player_type)
    random_instances = random.sample(list(all_instances), count)
    random_ids = [instance.pk for instance in random_instances]
    return random_ids

async def get_initial_shop_for_player(num_reaction_cards, num_action_cards, player_type):
    reaction_card_ids = await get_random_card_ids(ReactionCard, num_reaction_cards, player_type)
    action_card_ids = await get_random_card_ids(ActionCard, num_action_cards, player_type)

    return reaction_card_ids, action_card_ids