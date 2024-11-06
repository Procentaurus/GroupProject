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
        poison_turns=None,
        poison_damage=None,
        persistent_blocks=None,
):
    # Initialize or retrieve values from stored state
    acting_player_health = acting_player.morale
    reacting_player_health = reacting_player.morale

    if poison_turns is None:
        poison_turns = reacting_player.poison_turns
    if poison_damage is None:
        poison_damage = reacting_player.poison_damage
    if persistent_blocks is None:
        persistent_blocks = reacting_player.persistent_blocks

    # Retrieve action and reaction cards
    reaction_card_list = get_reaction_cards_from_dictionary(reaction_card_dictionary)
    action_card = ActionCard.objects.get(id=action_card_id)
    action_damage = calculate_action_damage(action_card)

    # Calculate reaction including persistent effects
    blocked_damage, redirected_damage, new_action_damage, poison_damage, poison_turns, persistent_blocks = calculate_reaction(
        action_damage, reaction_card_list
    )

    # Update health values
    new_acting_player_health = acting_player_health - redirected_damage
    new_reacting_player_health = reacting_player_health - (new_action_damage + blocked_damage)

    # Apply poison damage if active
    if poison_turns > 0:
        new_reacting_player_health -= poison_damage
        poison_turns -= 1

    # Update persistent blocks (carry over to next turn)
    new_persistent_blocks = persistent_blocks

    # Return new morale values and other status
    new_acting_player_money, new_reacting_player_money = (200, 200)

    return new_acting_player_health, new_acting_player_money, new_reacting_player_health, new_reacting_player_money, poison_turns, poison_damage, new_persistent_blocks

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