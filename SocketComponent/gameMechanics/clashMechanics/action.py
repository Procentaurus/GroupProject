import re

def calculate_action_damage(action_card):
    pattern = r'(\d+)\s+damage'
    match = re.search(pattern, action_card.description)
    damage = int(match.group(1))
    return damage

def apply_poison_effect(reacting_player_health, poison_damage, poison_turns):
    if poison_turns > 0:
        reacting_player_health -= poison_damage
        poison_turns -= 1
    return reacting_player_health, poison_turns
