import re
from gameMechanics.models import ReactionCard

def get_values_dict(values_string):
    dictionary = dict(re.findall(r'(\w+)[=:]([^\s,;]+)', values_string))
    return dictionary

def get_reaction_cards_from_dictionary(reaction_cards_dict):
    card_uuids = []

    for item in reaction_cards_dict:
        card_id = item['id']
        amount = item['amount']
        card_uuids.extend([card_id] * amount)

    reaction_cards = ReactionCard.objects.filter(pk__in=card_uuids)

    return list(reaction_cards)
