import re
from gameMechanics.models import ActionCard

def calculate_action_damage(action_card):
    pattern = r'(\d+)\s+damage'

    match = re.search(pattern, action_card.description)

    damage = int(match.group(1))
    return damage