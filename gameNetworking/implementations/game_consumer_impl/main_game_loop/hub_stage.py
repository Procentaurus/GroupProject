from gameMechanics.enums import PlayerState

from gameNetworking.enums import MessageType
from .checkers import *
from .purchasing_cards import purchase_action_card, purchase_reaction_card
from .surrender import surrender_move_mechanics

async def hub_stage_impl(consumer, game, game_stage, message_type, game_user, data):

    if message_type == MessageType.PURCHASE_MOVE:
        action_cards_ids = data.get("action_cards")
        reaction_cards_data = data.get("reaction_cards")
        await purchase_move_mechanics(
            consumer, game_user, action_cards_ids, reaction_cards_data)
    elif message_type == MessageType.READY_MOVE:
        await ready_move_mechanics(consumer, game, game_user)
    elif message_type == MessageType.SURRENDER_MOVE:
        await surrender_move_mechanics(consumer, game_user)
    else:
        await consumer.error(
            f"Wrong message type in the {game_stage} game stage.")

async def ready_move_mechanics(consumer, game, game_user):
    opponent = await game.get_opponent_player(game_user.id)

    # Check if player is in the state after reporting readyness 
    if game_user.state == PlayerState.AWAIT_CLASH_START:
        await consumer.error(consumer,
            "You have already declared readyness.",
            f"{game_user.conflict_side} player tried to declare readiness \
            for the clash afresh.")
        return
    
    # Check if player is in the hub stage, if not then flow error occured
    if game_user.state != PlayerState.IN_HUB:
        await consumer.critical_error(consumer,
            f"Improper state {game_user.state} of {game_user.conflict_side} \
            player in ready_move.")
        return
    
    if opponent.state == PlayerState.IN_HUB:
        await game_user.set_state(PlayerState.AWAIT_CLASH_START)
    elif opponent.state == PlayerState.AWAIT_CLASH_START:
        await consumer.send_message_to_group(
            {"next_move_player" : game.next_move_player},
            "clash_start")
    else:
        await consumer.critical_error(
            f"Improper opponent player state: {opponent.state}")

async def purchase_move_mechanics(
        consumer, game_user, action_cards_ids, reaction_cards_data):

    # Check if player is in the state after reporting readiness 
    if game_user.state == PlayerState.AWAIT_CLASH_START:
        await consumer.error(consumer,
            "You cannot purchase cards after declaring readiness for clash.",
            f"{game_user.conflict_side} player tried to purchase \
            cards after declaring readyness.")
        return
    
    # Check if player is in the hub stage, if not then flow error occured
    if game_user.state != PlayerState.IN_HUB:
        await consumer.critical_error(consumer,
            f"Improper state {game_user.state} of {game_user.conflict_side} \
            player in purchase_move.")
        return

    reaction_cards_ids = {x.get("reaction_card_id") for x in reaction_cards_data}

    all_action_cards_exist = await check_all_action_cards_exist(
        consumer, action_cards_ids)
    if not all_action_cards_exist: return

    all_reaction_cards_exist = await check_all_reaction_cards_exist(
        consumer, reaction_cards_ids)
    if not all_reaction_cards_exist: return

    all_cards_are_in_shop = await check_all_cards_are_in_shop(
        consumer, game_user, action_cards_ids, reaction_cards_data)
    if not all_cards_are_in_shop: return

    user_can_afford_all_cards = await check_game_user_can_afford_all_cards(
        consumer, game_user, action_cards_ids, reaction_cards_data)
    if not user_can_afford_all_cards: return

    for action_card_id in action_cards_ids:
        _ = await purchase_action_card(consumer, game_user, action_card_id)

    for reaction_card_data in reaction_cards_data:
        _ = await purchase_reaction_card(
            consumer, game_user, reaction_card_data.get("reaction_card_id"),
            reaction_card_data.get("amount"))
        
    await consumer.purchase_result({"new_money_amount" : game_user.money})
