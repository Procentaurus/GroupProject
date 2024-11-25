import pytest
from clashMechanics.cards import Card, ActionCard, ReactionCard, CardFactory

def test_card_initialization():
    card = Card(name="Test Card", description="A test card", price=5, player_type="student")
    assert card.name == "Test Card"
    assert card.description == "A test card"
    assert card.price == 5
    assert card.player_type == "student"

def test_action_card_damage_calculation():
    action_card = ActionCard(name="Damage Card", description="Deal 10 damage", price=3, player_type="teacher", pressure=2)
    damage = action_card.calculate_damage()
    assert damage == 10

def test_reaction_card_value_parsing():
    reaction_card = ReactionCard(
        name="Block Card",
        description="Blocks damage",
        values="block=10;redirect=5",
        price=4,
        player_type="student",
        card_type="Brute"
    )
    assert reaction_card.values["block"] == "10"
    assert reaction_card.values["redirect"] == "5"

def test_reaction_card_apply_reaction():
    reaction_card = ReactionCard(
        name="Complex Reaction",
        description="Complex effects",
        values="block=10;redirect=5;percentage_value=blocked;percentage=10",
        price=5,
        player_type="teacher",
        card_type="Intelligence"
    )
    remaining_damage, redirected_damage = reaction_card.apply_reaction(100)
    assert remaining_damage == 80  # 100 - 10 block - 10% of 100 block
    assert redirected_damage == 5

def test_card_factory_action_card():
    card_data = {
        "model": "gameMechanics.actioncard",
        "fields": {
            "name": "Action Test",
            "description": "Deal 20 damage",
            "price": "5",
            "playerType": "student",
            "pressure": "3",
        }
    }
    card = CardFactory.create_card(card_data)
    assert isinstance(card, ActionCard)
    assert card.name == "Action Test"
    assert card.calculate_damage() == 20

def test_card_factory_reaction_card():
    card_data = {
        "model": "gameMechanics.reactioncard",
        "fields": {
            "name": "Reaction Test",
            "description": "Blocks and redirects",
            "values": "block=15;redirect=10",
            "price": "4",
            "playerType": "teacher",
            "type": "Brute",
        }
    }
    card = CardFactory.create_card(card_data)
    assert isinstance(card, ReactionCard)
    assert card.values["block"] == "15"
    assert card.values["redirect"] == "10"
