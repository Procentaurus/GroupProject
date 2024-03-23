from gameNetworking.enums import PlayerState, MessageType
from .checkers import *
from .purchasing_cards import purchase_action_card, purchase_reaction_card
from .common import surrender_move_mechanics, inform_about_improper_state_error

async def hub_stage_impl(consumer, game, message_type, data):

    if message_type == MessageType.PURCHASE_MOVE:
        action_cards_ids = data.get("action_cards")
        reaction_cards_data = data.get("reaction_cards")
        await purchase_move_mechanics(
            consumer, action_cards_ids, reaction_cards_data)
    elif message_type == MessageType.READY_MOVE:
        await ready_move_mechanics(consumer, game)
    elif message_type == MessageType.SURRENDER_MOVE:
        await surrender_move_mechanics(consumer)
    else:
        await consumer.error(
            f"Wrong message type in the {consumer.get_game_stage()}"
            +" game stage.")

async def ready_move_mechanics(consumer, game):

    game_user = consumer.get_game_user()

    if is_player_awaiting_clash(game_user):
        await inform_cards_cannot_be_bought_when_await_clash(consumer)
        return
    
    if not is_player_in_hub(game_user):
        await inform_about_improper_state_error(consumer, "ready_move")
        return
    
    opponent = await game.get_opponent_player(game_user.id)
    if is_player_in_hub(opponent):
        await game_user.set_state(PlayerState.AWAIT_CLASH_START)
    elif is_player_awaiting_clash(opponent):
        await consumer.send_message_to_group(
            {"next_move_player" : game.next_move_player},
            "clash_start")
    else:
        await consumer.critical_error(
            f"Improper opponent player state: {opponent.state}")

async def purchase_move_mechanics(
    consumer, action_cards_ids, reaction_cards_data):

    game_user = consumer.get_game_user()

    if is_player_awaiting_clash(game_user):
        await inform_cards_cannot_be_bought_when_await_clash(consumer)
        return
    
    if not is_player_in_hub(game_user):
        await inform_about_improper_state_error(consumer, "purchase_move")
        return
    
    if not await check_all_action_cards_exist(consumer, action_cards_ids):
        return

    if not await check_all_reaction_cards_exist(consumer,
        {x.get("reaction_card_id") for x in reaction_cards_data}): return

    if not await check_all_cards_are_in_shop(
        consumer, action_cards_ids, reaction_cards_data): return

    if not await check_game_user_can_afford_all_cards(
        consumer, action_cards_ids, reaction_cards_data): return
    
    for action_card_id in action_cards_ids:
        _ = await purchase_action_card(consumer, action_card_id)

    for reaction_card_data in reaction_cards_data:
        _ = await purchase_reaction_card(
            consumer, reaction_card_data.get("reaction_card_id"),
            reaction_card_data.get("amount"))
        
    await consumer.purchase_result({"new_money_amount" : game_user.money})

def is_player_awaiting_clash(game_user):
    return game_user.state == PlayerState.AWAIT_CLASH_START

def is_player_in_hub(game_user):
    return game_user.state == PlayerState.IN_HUB

async def inform_cards_cannot_be_bought_when_await_clash(consumer):
    await consumer.error("You have already declared readyness.",
        f"{consumer.get_game_user().conflict_side} player tried to declare"
        +" readyness for the clash afresh.")
