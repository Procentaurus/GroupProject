from gameMechanics.models import ActionCard
from channels.db import database_sync_to_async
from .reaction import calculate_reaction
from .utils import get_reaction_cards_from_dictionary
from .action import calculate_action_damage

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

async def get_rerolled_cards(game_user):
    pass

@database_sync_to_async
def get_mock_action_card_id(player_type):
    if player_type == 'teacher':
        return ActionCard.objects.get(name='Insult the student').id
    elif player_type == 'student':
        return ActionCard.objects.get(name='Insult the teacher').id
    else:
        raise ValueError("Invalid player type")