import re
from gameMechanics.models import ActionCard, ReactionCard
from channels.db import database_sync_to_async

# TODO: Convert mechanics into classes that implement them instead of simple functions
# TODO: Adjust database fields to operate on values instead of parsing them from descriptions

# dict values:
#  - conditional_value
#  - conditional_threshhold
#  - block
#  - redirect
#  - percentage_value
#  - percentage

# Calculate health for each player after each instance of action-reaction during a clash
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
    action_card = ActionCard.objects.get(id = action_card_id)
    action_damage = calculate_action_damage(action_card)
    blocked_damage, redirected_damage, new_action_damage = calculate_reaction(action_damage, reaction_card_list)
    new_acting_player_health = acting_player_health - redirected_damage
    new_reacting_player_health = reacting_player_health - (new_action_damage + blocked_damage)
    new_acting_player_money, new_reacting_player_money = (200, 200)
    
    return new_acting_player_health, new_acting_player_money, new_reacting_player_health, new_reacting_player_money

# Placeholder function for damage calculation
# TODO: Replace with more complex mechanics for action damage
def calculate_action_damage(action_card):
    pattern = r'(\d+)\s+damage'

    # Search for the pattern in the description
    match = re.search(pattern, action_card.description)

    damage = int(match.group(1))  # Extract the numeric value    
    return damage

# Most important function of this script
# Used to calculate reaction mechanics based on predetermined values dictionary
def calculate_reaction(action_damage, reaction_card_list):

    blocked_damage = 0
    redirected_damage = 0

    for reaction_card in reaction_card_list:
        
        values_string = reaction_card.values
        values_dictionary = get_values_dict(values_string)
        condition_satisfied = True
        
        # A switch to iterate through the values dictionary
        # TODO: Implement a more elegant solution
        for key, value in values_dictionary.items():
            if key == 'conditional_value':
                conditional_value = value
                pass
            elif key == 'conditional_threshhold':
                if conditional_value == 'blocked':
                    if blocked_damage <= int(value):
                        condition_satisfied = False
                elif conditional_value == 'redirected':
                    if redirected_damage <= int(value):
                        condition_satisfied = False
                pass
            elif key == 'redirect':
                if condition_satisfied:
                    redirected_damage += int(value)
                pass
            elif key == 'block':
                if condition_satisfied:
                    blocked_damage += int(value)
                pass
            elif key == 'percentage_value':
                percentage_value = value
            elif key == 'percentage':
                if condition_satisfied:
                    if percentage_value == 'blocked':
                        blocked_damage += action_damage*0.01*int(value)
                    elif percentage_value == 'redirected':
                        redirected_damage += redirected_damage*0.01*int(value)
                pass

    return blocked_damage, redirected_damage, action_damage - blocked_damage

def get_reaction_cards_from_dictionary(reaction_cards_dict):
    card_uuids = []

    for item in reaction_cards_dict:
        card_id = item['id']
        amount = item['amount']
        card_uuids.extend([card_id] * amount)

    reaction_cards = ReactionCard.objects.filter(pk__in=card_uuids)

    return list(reaction_cards)

def get_values_dict(values_string):
    dictionary = dict(re.findall(r'(\w+)[=:]([^\s,;]+)', values_string))
    return dictionary

async def get_rerolled_cards(game_user):
    pass

def get_mock_action_card(player_type):
    if player_type == 'teacher':
        return ActionCard.objects.get(name='Insult the student')
    elif player_type == 'student':
        return ActionCard.objects.get(name='Insult the teacher')
    else:
        raise ValueError("Invalid player type")

# TODO: Consult usage
def get_action_cards():
    return None

def get_reaction_cards():
    return None
