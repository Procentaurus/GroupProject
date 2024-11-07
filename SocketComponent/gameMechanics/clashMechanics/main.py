import random
from gameMechanics.models import ActionCard, ReactionCard
from channels.db import database_sync_to_async
from .reaction import calculate_reaction
from .utils import get_reaction_cards_from_dictionary
from .action import calculate_action_damage
from gameMechanics.serializers import ReactionCardDataSerializer, ActionCardDataSerializer
from gameNetworking.models.queries import get_reaction_cards_in_shop

@database_sync_to_async
def get_new_morale(
        reacting_player,
        acting_player,
        action_card_id,
        reaction_card_dictionary,
):
    acting_player_health = acting_player.morale
    reacting_player_health = reacting_player.morale
    reaction_card_list = get_reaction_cards_from_dictionary(reaction_card_dictionary)
    action_card = ActionCard.objects.get(id=action_card_id)
    action_damage = calculate_action_damage(action_card)
    blocked_damage, redirected_damage, new_action_damage = calculate_reaction(action_damage, reaction_card_list)
    new_acting_player_health = acting_player_health - redirected_damage
    new_reacting_player_health = reacting_player_health - (new_action_damage + blocked_damage)
    new_acting_player_money, new_reacting_player_money = (200, 200)
    
    return new_acting_player_health, new_acting_player_money, new_reacting_player_health, new_reacting_player_money

@database_sync_to_async
def get_filtered_card_ids(model, player_type):
    return list(model.objects.filter(playerType=player_type).exclude(name__in=["Insult the teacher", "Insult the student"]).values_list('id', flat=True))

async def get_rerolled_cards(game_user):
    # Fetch current action and reaction cards in the shop
    current_action_cards = await game_user.get_action_cards_in_shop()
    current_reaction_cards = await get_reaction_cards_in_shop(game_user)
    print("Current action cards")
    print(current_action_cards)
    print("Current reaction cards")
    print(current_reaction_cards)
    
    # Fetch all available action and reaction cards, filtering out mock cards and based on playerType
    if game_user.is_teacher():
        player_type = 'teacher'
    elif game_user.is_student():
        player_type = 'student'
    all_action_card_ids = await get_filtered_card_ids(ActionCard, player_type)
    all_reaction_card_ids = await get_filtered_card_ids(ReactionCard, player_type)

    print("All action card ids")
    print(all_action_card_ids)
    print("All reaction card ids")
    print(all_reaction_card_ids)
    
    # Remove current shop cards from all cards to increase the chance of picking new ones
    current_action_card_ids = [card.id for card in current_action_cards]
    current_reaction_card_ids = [c['card'].id for c in current_reaction_cards]
    available_action_card_ids = [card_id for card_id in all_action_card_ids if card_id not in current_action_card_ids]
    available_reaction_card_ids = [card_id for card_id in all_reaction_card_ids if card_id not in current_reaction_card_ids]
    print("Available action card ids")
    print(available_action_card_ids)
    print("Available reaction card ids")
    print(available_reaction_card_ids)
    
    # Randomly select new cards for the shop
    new_action_card_ids = random.sample(available_action_card_ids, len(current_action_card_ids))
    new_reaction_cards = []
    for _ in range(len(current_reaction_card_ids)):
        card_id = random.choice(available_reaction_card_ids)
        amount = random.randint(1, 5)  # Assuming the amount can be between 1 and 5
        new_reaction_cards.append({'card_id': card_id, 'amount': amount})
    print("New action card ids")
    print(new_action_card_ids)
    
    # Serialize new cards
    serialized_new_action_cards = ActionCardDataSerializer(ActionCard.objects.filter(id__in=new_action_card_ids), many=True).data
    serialized_new_reaction_cards = [
        {'card': ReactionCardDataSerializer(ReactionCard.objects.get(id=card['card_id'])).data, 'amount': card['amount']}
        for card in new_reaction_cards
    ]
    print("Serialized new action cards")
    print(serialized_new_action_cards)
    print("Serialized new reaction cards")
    print(serialized_new_reaction_cards)
    
    return {
        "new_action_cards": serialized_new_action_cards,
        "new_reaction_cards": serialized_new_reaction_cards
    }

@database_sync_to_async
def get_mock_action_card_id(player_type):
    if player_type == 'teacher':
        return ActionCard.objects.get(name='Insult the student').id
    elif player_type == 'student':
        return ActionCard.objects.get(name='Insult the teacher').id
    else:
        raise ValueError("Invalid player type")