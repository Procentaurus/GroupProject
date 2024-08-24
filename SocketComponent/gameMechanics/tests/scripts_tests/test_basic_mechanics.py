import pytest
from gameMechanics.scripts.basic_mechanics import *

# TODO: Fix the use of parametrize
@pytest.mark.parametrize("action_damage, reaction_card_list, expected_blocked_damage, expected_redirected_damage, expected_new_action_damage", [
    (10, [{"values": "conditional_value=blocked;conditional_threshhold=5;block=10"},
          {"values": "block=2"},
          {"values": "redirect=2;block=2"}],
     4, 2, 4),
    (20, [{"values": "block=5"},
          {"values": "conditional_value=blocked;conditional_threshhold=4;redirect=10;block=10"}],
     15, 10, 5),
])
def test_calculate_reaction(action_damage, reaction_card_list, expected_blocked_damage, expected_redirected_damage, expected_new_action_damage):
    blocked_damage, redirected_damage, new_action_damage = calculate_reaction(action_damage, reaction_card_list)
    assert blocked_damage == expected_blocked_damage
    assert redirected_damage == expected_redirected_damage
    assert new_action_damage == expected_new_action_damage
