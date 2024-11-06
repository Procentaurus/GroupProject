from gameMechanics.clashMechanics.utils import get_values_dict


def handle_block(value, action_damage, blocked_damage, redirected_damage, condition_satisfied, percentage_value):
    if condition_satisfied:
        blocked_damage += int(value)
    return blocked_damage, redirected_damage

def handle_redirect(value, action_damage, blocked_damage, redirected_damage, condition_satisfied, percentage_value):
    if condition_satisfied:
        redirected_damage += int(value)
        blocked_damage += int(value)
    return blocked_damage, redirected_damage

def handle_percentage(value, action_damage, blocked_damage, redirected_damage, condition_satisfied, percentage_value):
    if condition_satisfied:
        if percentage_value == 'blocked':
            blocked_damage += action_damage * 0.01 * int(value)
        elif percentage_value == 'redirected':
            redirected_damage += redirected_damage * 0.01 * int(value)
    return blocked_damage, redirected_damage

reaction_handlers = {
    'block': handle_block,
    'redirect': handle_redirect,
    'percentage': handle_percentage
}

def calculate_reaction(action_damage, reaction_card_list):
    blocked_damage = 0
    redirected_damage = 0

    for reaction_card in reaction_card_list:
        values_string = reaction_card.values
        values_dictionary = get_values_dict(values_string)
        condition_satisfied = True

        conditional_value = None
        percentage_value = None

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
            elif key in reaction_handlers:
                blocked_damage, redirected_damage = reaction_handlers[key](
                    value, action_damage, blocked_damage, redirected_damage, condition_satisfied, percentage_value
                )

    return blocked_damage, redirected_damage, action_damage - blocked_damage