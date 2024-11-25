import pytest
from gameMechanics.clashMechanics.cards import ActionCard, ReactionCard, CardFactory

@pytest.fixture
def sample_action_card():
    return {
        "model": "gameMechanics.actioncard",
        "fields": {
            "name": "Power Punch",
            "description": "Deal 20 damage",
            "price": 5,
            "playerType": "student",
            "pressure": 2
        }
    }

@pytest.fixture
def sample_reaction_card():
    return {
        "model": "gameMechanics.reactioncard",
        "fields": {
            "name": "Shield Block",
            "description": "Block incoming damage",
            "values": "block=10;conditional_value=blocked;conditional_threshold=5",
            "price": 3,
            "playerType": "student",
            "type": "Brute"
        }
    }

### Testy dla ActionCard ###
def test_action_card_initialization(sample_action_card):
    action_card = CardFactory.create_card(sample_action_card)
    assert action_card.name == "Power Punch"
    assert action_card.description == "Deal 20 damage"
    assert action_card.price == 5
    assert action_card.player_type == "student"
    assert action_card.pressure == 2

def test_action_card_damage_calculation(sample_action_card):
    action_card = CardFactory.create_card(sample_action_card)
    damage = action_card.calculate_damage()
    assert damage == 20

### Testy dla ReactionCard ###
def test_reaction_card_initialization(sample_reaction_card):
    reaction_card = CardFactory.create_card(sample_reaction_card)
    assert reaction_card.name == "Shield Block"
    assert reaction_card.description == "Block incoming damage"
    assert reaction_card.price == 3
    assert reaction_card.player_type == "student"
    assert reaction_card.card_type == "Brute"
    assert reaction_card.values == {
        "block": "10",
        "conditional_value": "blocked",
        "conditional_threshold": "5"
    }

def test_reaction_card_apply_reaction_block_effect():
    reaction_card = ReactionCard(
        name="Shield Block",
        description="Block incoming damage",
        values="block=10",
        price=3,
        player_type="student",
        card_type="Brute"
    )
    remaining_damage, redirected_damage = reaction_card.apply_reaction(20)
    assert remaining_damage == 10
    assert redirected_damage == 0

def test_reaction_card_apply_reaction_conditional_threshold():
    reaction_card = ReactionCard(
        name="Shield Block",
        description="Conditional blocking",
        values="block=10;conditional_value=blocked;conditional_threshold=15",
        price=3,
        player_type="student",
        card_type="Brute"
    )
    # Below threshold: effect not applied
    remaining_damage, redirected_damage = reaction_card.apply_reaction(20)
    assert remaining_damage == 20
    assert redirected_damage == 0

def test_reaction_card_apply_percentage_modifications():
    reaction_card = ReactionCard(
        name="Percentage Shield",
        description="Blocks a percentage of damage",
        values="percentage_value=blocked;percentage=50",
        price=4,
        player_type="student",
        card_type="Intelligence"
    )
    remaining_damage, redirected_damage = reaction_card.apply_reaction(40)
    assert remaining_damage == 20  # Blocks 50% of 40
    assert redirected_damage == 0

### Testy dla CardFactory ###
def test_card_factory_creates_action_card(sample_action_card):
    card = CardFactory.create_card(sample_action_card)
    assert isinstance(card, ActionCard)

def test_card_factory_creates_reaction_card(sample_reaction_card):
    card = CardFactory.create_card(sample_reaction_card)
    assert isinstance(card, ReactionCard)

def test_card_factory_raises_error_for_invalid_card_type():
    invalid_card_data = {
        "model": "gameMechanics.unknowncard",
        "fields": {
            "name": "Unknown Card",
            "description": "Unknown effect",
            "price": 1,
            "playerType": "student"
        }
    }
    with pytest.raises(ValueError, match="Unknown card type"):
        CardFactory.create_card(invalid_card_data)
