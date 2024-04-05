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
async def get_new_morale(
        reacting_player,
        acting_player,
        action_card_id,
        reaction_card_dictionary,
):
    acting_player_health = acting_player.morale
    reacting_player_health = reacting_player.morale
    reaction_card_list = await get_reaction_cards_from_dictionary(reaction_card_dictionary)
    action_card = await database_sync_to_async(ActionCard.objects.get(id = action_card_id))
    action_damage = await calculate_action_damage(action_card)
    blocked_damage, redirected_damage, new_action_damage = await calculate_reaction(action_damage, reaction_card_list)
    new_acting_player_health = acting_player_health - redirected_damage
    new_reacting_player_health = reacting_player_health - (new_action_damage + blocked_damage)
    new_acting_player_money, new_reacting_player_money = 200
    
    return new_acting_player_health, new_acting_player_money, new_reacting_player_health, new_reacting_player_money

# Placeholder function for damage calculation
# TODO: Replace with more complex mechanics for action damage
async def calculate_action_damage(action_card):
    damage = action_card.damage

# Most important function of this script
# Used to calculate reaction mechanics based on predetermined values dictionary
async def calculate_reaction(action_damage, reaction_card_list):

    blocked_damage = 0
    redirected_damage = 0

    for reaction_card in reaction_card_list:
        
        values_string = reaction_card.get("values")
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

@database_sync_to_async
def get_reaction_cards_from_dictionary(card_dictionary):
    # Extract UUIDs from the keys of the dictionary and create a flat list
    card_uuids = [uuid for uuid, count in card_dictionary.items() for _ in range(count)]

    # Query ReactionCard objects from the database based on UUIDs
    reaction_cards = ReactionCard.objects.filter(pk__in=card_uuids)

    # Convert the queryset to a list
    reaction_card_list = list(reaction_cards)

    return reaction_card_list

def get_values_dict(values_string):
    dictionary = dict(re.findall(r'(\w+)[=:]([^\s,;]+)', values_string))
    return dictionary

# TODO: Consult usage
def get_action_cards():
    return None

def get_reaction_cards():
    return None
