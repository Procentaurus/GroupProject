from gameMechanics.clashMechanics.utils import get_values_dict

def handle_block(value, blocked_damage, redirected_damage, condition_satisfied):
    if condition_satisfied:
        blocked_damage += int(value)
    return blocked_damage, redirected_damage

def handle_redirect(value, blocked_damage, redirected_damage, condition_satisfied):
    if condition_satisfied:
        redirected_damage += int(value)
    return blocked_damage, redirected_damage

def handle_percentage(value, action_damage, blocked_damage, redirected_damage, condition_satisfied, percentage_value):
    if condition_satisfied:
        if percentage_value == 'blocked':
            blocked_damage += action_damage * 0.01 * int(value)
        elif percentage_value == 'redirected':
            redirected_damage += redirected_damage * 0.01 * int(value)
    return blocked_damage, redirected_damage

def handle_poison(value, poison_damage, poison_turns, condition_satisfied):
    if condition_satisfied:
        poison_damage += int(value)
        poison_turns = 3  # Fixed duration for poison effect
    return poison_damage, poison_turns

def handle_duration(value, persistent_blocks, condition_satisfied):
    if condition_satisfied:
        persistent_blocks.append(int(value))  # Add block value for future turns
    return persistent_blocks

def handle_synergy(value, synergy_active, synergy_bonus, condition_satisfied):
    if condition_satisfied:
        synergy_active = True
        synergy_bonus += int(value)
    return synergy_active, synergy_bonus

def handle_synergy_bonus(value, redirected_damage, blocked_damage, poison_damage, synergy_active, condition_satisfied, mechanic_type):
    if condition_satisfied and synergy_active:
        if mechanic_type == 'redirect':
            redirected_damage += int(value)
        elif mechanic_type == 'block':
            blocked_damage += int(value)
        elif mechanic_type == 'poison':
            poison_damage += int(value)
    return redirected_damage, blocked_damage, poison_damage

reaction_handlers = {
    'block': handle_block,
    'redirect': handle_redirect,
    'percentage': handle_percentage,
    'poison': handle_poison,
    'duration': handle_duration,
    'synergy': handle_synergy,
    'synergy_bonus': handle_synergy_bonus
}

def calculate_reaction(action_damage, reaction_card_list):
    blocked_damage = 0
    redirected_damage = 0
    poison_damage = 0
    poison_turns = 0
    persistent_blocks = []
    synergy_active = False
    synergy_bonus = 0

    for reaction_card in reaction_card_list:
        values_string = reaction_card.values
        values_dictionary = get_values_dict(values_string)
        condition_satisfied = True

        conditional_value = None
        percentage_value = None
        mechanic_type = None

        for key, value in values_dictionary.items():
            if key == 'conditional_value':
                conditional_value = value
            elif key == 'conditional_threshhold':
                if conditional_value == 'blocked':
                    if blocked_damage <= int(value):
                        condition_satisfied = False
                elif conditional_value == 'redirected':
                    if redirected_damage <= int(value):
                        condition_satisfied = False
            elif key == 'percentage_value':
                percentage_value = value
            elif key == 'mechanic_type':
                mechanic_type = value
            elif key in reaction_handlers:
                if key == 'poison':
                    poison_damage, poison_turns = reaction_handlers[key](
                        value, poison_damage, poison_turns, condition_satisfied
                    )
                elif key == 'duration':
                    persistent_blocks = reaction_handlers[key](value, persistent_blocks, condition_satisfied)
                elif key == 'synergy':
                    synergy_active, synergy_bonus = reaction_handlers[key](value, synergy_active, synergy_bonus, condition_satisfied)
                elif key == 'synergy_bonus':
                    redirected_damage, blocked_damage, poison_damage = reaction_handlers[key](
                        value, redirected_damage, blocked_damage, poison_damage, synergy_active, condition_satisfied, mechanic_type
                    )
                else:
                    blocked_damage, redirected_damage = reaction_handlers[key](
                        value, action_damage, blocked_damage, redirected_damage, condition_satisfied, percentage_value
                    )

    if synergy_active:
        redirected_damage += synergy_bonus

    return blocked_damage, redirected_damage, action_damage - blocked_damage, poison_damage, poison_turns, persistent_blocks
