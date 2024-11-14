from channels.db import database_sync_to_async
from gameMechanics.models import ActionCard as DBActionCard
from .utils import load_cards_for_clash
from .cards import CardFactory

@database_sync_to_async
def get_new_morale(
        reacting_player,
        acting_player,
        action_card_id,
        reaction_card_dictionary,
):
    # Retrieve player health
    acting_player_health = acting_player.morale
    reacting_player_health = reacting_player.morale
    
    # Convert reaction_card_dictionary to IDs for loading
    reaction_card_ids = [item['id'] for item in reaction_card_dictionary]

    # Load in-memory ActionCard and ReactionCard instances for the clash
    action_card, reaction_cards = load_cards_for_clash(action_card_id, reaction_card_ids)

    # Calculate initial action damage
    action_damage = action_card.calculate_damage()

    # Apply each reaction card's effect to modify action damage
    for reaction_card in reaction_cards:
        action_damage, redirected_damage = reaction_card.apply_reaction(action_damage)

    # Calculate final health values after clash
    new_acting_player_health = acting_player_health - redirected_damage
    new_reacting_player_health = reacting_player_health - action_damage
    
    # Placeholder money values (can adjust as needed for actual game mechanics)
    new_acting_player_money, new_reacting_player_money = 200, 200

    return new_acting_player_health, new_acting_player_money, new_reacting_player_health, new_reacting_player_money

@database_sync_to_async
def get_mock_action_card_id(player_type):
    # Retrieve a mock action card ID based on player type
    if player_type == 'teacher':
        return DBActionCard.objects.get(name='Insult the student').id
    elif player_type == 'student':
        return DBActionCard.objects.get(name='Insult the teacher').id
    else:
        raise ValueError("Invalid player type")
