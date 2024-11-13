import re
from gameMechanics.models import ActionCard as DBActionCard, ReactionCard as DBReactionCard
from .cards import CardFactory

def load_cards_for_clash(action_card_id, reaction_card_ids):
    # Load the action card from the database
    db_action_card = DBActionCard.objects.get(id=action_card_id)
    action_card_data = {
        "model": "gameMechanics.actioncard",
        "fields": db_action_card.__dict__
    }
    action_card = CardFactory.create_card(action_card_data)

    # Load the reaction cards from the database
    db_reaction_cards = DBReactionCard.objects.filter(id__in=reaction_card_ids)
    reaction_cards = [
        CardFactory.create_card({
            "model": "gameMechanics.reactioncard",
            "fields": db_reaction_card.__dict__
        })
        for db_reaction_card in db_reaction_cards
    ]

    return action_card, reaction_cards

def get_reaction_cards_ids_from_dictionary(reaction_cards_dict):
    card_uuids = []

    for item in reaction_cards_dict:
        card_id = item['id']
        amount = item['amount']
        card_uuids.extend([card_id] * amount)

    return list(card_uuids)
