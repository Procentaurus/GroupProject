from gameMechanics.enums import PlayerState, GameStage

from gameNetworking.implementations.game_consumer_impl.purchasing import *
from gameNetworking.implementations.game_consumer_impl.checkers import *
from gameNetworking.enums import MessageType
from gameNetworking.queries import *

# Main game loop function responsible for taking care of user requests to socket
async def main_game_loop_impl(consumer, data):

    if consumer.get_game_id() is not None: # has game started or not

        message_type = data.get('type')
        game_id = consumer.get_game_id()
        game_user = await get_game_user(consumer.get_game_user_id())
        game_stage = consumer.get_game_stage()

        if game_stage == GameStage.HUB:
            await hub_stage_impl(consumer, game_id, message_type, game_user, data) 
        else:
            await clash_stage_impl(consumer, game_id, message_type, game_user, data)
    else:
        await consumer.error(
            f"{game_user.conflict_side} player made move before the game has started")

async def clash_stage_impl(consumer, message_type, game_id, game_user, data):

    if message_type == MessageType.CLASH_ACTION_MOVE:
        action_card_id = data.get("action_card")
        await clash_action_move_mechanics(consumer, game_id, game_user, action_card_id)
    elif message_type == MessageType.CLASH_REACTION_MOVE:
        reaction_cards_data = data.get("reaction_cards")
        await clash_reaction_move_mechanics(
            consumer, game_id, game_user, reaction_cards_data)
    elif message_type == MessageType.SURRENDER_MOVE:
        await surrender_move_mechanics(consumer, game_user)
    else:
        await consumer.error(
            f"Wrong message type in the {consumer.get_game_stage()} game stage.")
        
async def hub_stage_impl(consumer, game_id, message_type, game_user, data):

    if message_type == MessageType.PURCHASE_MOVE:
        await purchase_move_mechanics(consumer, game_user, data)
    elif message_type == MessageType.READY_MOVE:
        await ready_move_mechanics(consumer, game_id, game_user, data)
    elif message_type == MessageType.SURRENDER_MOVE:
        await surrender_move_mechanics(consumer, game_user)
    else:
        await consumer.error(
            f"Wrong message type in the {consumer.get_game_stage()} game stage.")

async def surrender_move_mechanics(consumer, game_user):
    consumer.logger.info(f"{game_user.conflict_side} player has surrendered.")

    winner = "student" if game_user.conflict_side == "teacher" else "teacher"
    await consumer.send_message_to_group(
        {"winner": winner, 
        "after_surrender": True},
        "game_end")
    await consumer.cleanup()

async def ready_move_mechanics(consumer, game_id, game_user):
    game = await get_game(game_id)
    opponent = await game.get_opponent_player(game_user.id)

    # Check if player is in the state after reporting readiness 
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

async def purchase_move_mechanics(consumer, game_user, data):

    # Check if player is in the state after reporting readiness 
    if game_user.state == PlayerState.AWAIT_CLASH_START:
        await consumer.error(consumer,
            "You cannot purchase cards after declaring readiness for clash.",
            f"{game_user.conflict_side} player tried to purchase \
            cards after declaring readiness.")
        return
    
    # Check if player is in the hub stage, if not then flow error occured
    if game_user.state != PlayerState.IN_HUB:
        await consumer.critical_error(consumer,
            f"Improper state {game_user.state} of {game_user.conflict_side} \
            player in purchase_move.")
        return

    action_cards_ids = data.get("action_cards")
    reaction_cards_data = data.get("reaction_cards")
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

async def clash_action_move_mechanics(consumer, game_id, game_user, action_card_id):

    game = await get_game(game_id)
    moves_table = consumer.get_moves_table()
    if game.next_move_player != game_user.conflict_side:
        await consumer.error("Not your turn.",
            f"{game_user.conflict_side} player performed move \
            while it was not his turn.")
        return

    if game.next_move_type != "action":
        await consumer.error(
            "Wrong move. It is time for reaction."
            f"{game_user.conflict_side} player performed move of wrong type.")
        return
    
    # Check if player is in the clash stage, if not then flow error occured
    if game_user.state != PlayerState.IN_CLASH:
        await consumer.critical_error(consumer,
            f"Improper state {game_user.state} of {game_user.conflict_side} \
            player in clash action move.")
        return
    
    # Check if player have any action moves left in the clash
    if moves_table[0] == 0:
        await consumer.error(
            "You have no more action moves in this clash."
            f"{game_user.conflict_side} player performed action move while he had \
            none left")
        return
    
    action_card_exist = await check_all_action_cards_exist(consumer, [action_card_id])
    if not action_card_exist: return

    action_card_is_owned = await check_game_user_own_action_card(
        consumer, game_user, action_card_id)
    if not action_card_is_owned: return

    moves_table[0] -= 1 # 0 is index of action moves

    updated_game_turn = await update_game_turn(game_id)
    if not updated_game_turn:
        await consumer.critical_error("Updating game turn impossible.")
    else:
        await game_user.remove_action_card(action_card_id)
        await consumer.send_message_to_opponent(
            {"action_card" : action_card_id},
            "opponent_move")
        if moves_table[0] == 0: # player has no more action moves in the current clash
            await game_user.set_state(PlayerState.AWAIT_CLASH_END)

async def clash_reaction_move_mechanics(
        consumer, game_id, game_user, reaction_cards_data):

    game = await get_game(game_id)
    moves_table = consumer.get_moves_table()
    if game.next_move_player != game_user.conflict_side:
        await consumer.error("Not your turn.",
            f"{game_user.conflict_side} player performed move \
            while it was not his turn.")
        return

    if game.next_move_type != "action":
        await consumer.error(
            "Wrong move. It is time for action."
            f"{game_user.conflict_side} player performed move of wrong type.")
        return
    
    # Check if player is in the clash stage, if not then flow error occured
    if game_user.state != PlayerState.IN_CLASH \
        and game_user.state != PlayerState.AWAIT_CLASH_END:
        await consumer.critical_error(consumer,
            f"Improper state {game_user.state} of {game_user.conflict_side} \
            player in clash action move.")
        return
    
    reaction_cards_ids = {x.get("reaction_card_id") for x in reaction_cards_data}
    reaction_card_exist = await check_all_reaction_cards_exist(
        consumer, reaction_cards_ids)
    if not reaction_card_exist: return

    reaction_cards_are_owned = await check_game_user_own_reaction_cards(
        consumer, game_user, reaction_cards_data)
    if not reaction_cards_are_owned: return

    updated_game_turn = await update_game_turn(game_id)
    if not updated_game_turn:
        await consumer.critical_error("Updating game turn impossible.")
        return

    moves_table[1] -= 1 # 1 is index of reaction moves

    #TODO call functiosn that return needed values
    new_player_morale, new_opponent_morale = None, None
    money_player_gained, money_opponent_gained = None, None
    action_cards_player_gained, action_cards_opponent_gained = None, None
    reaction_cards_player_gained, reaction_cards_opponent_gained = None, None

    for reaction_card_data in reaction_cards_data:
        await game_user.remove_reaction_card(game_user,
            reaction_card_data.get("reaction_card_id"),
            reaction_card_data.get("amount"))

    await consumer.send_message_to_opponent(
        {"reaction_cards" : reaction_cards_data},
        "opponent_move")
    await consumer.clash_result({
        "new_player_morale" : new_player_morale,
        "new_opponent_morale" : new_opponent_morale,
        "money_gained" : money_player_gained,
        "action_cards_gained" : action_cards_player_gained,
        "reaction_cards_gained" : reaction_cards_player_gained
    })
    await consumer.send_message_to_opponent({
        "new_player_morale" : new_opponent_morale,
        "new_opponent_morale" : new_player_morale,
        "money_gained" : money_opponent_gained,
        "action_cards_gained" : action_cards_opponent_gained,
        "reaction_cards_gained" : reaction_cards_opponent_gained
    },"clash_result")

    opponent = await game.get_opponent_player(game_user.id)
    await add_gains_to_account(
        game_user, new_player_morale, money_player_gained,
        action_cards_player_gained, reaction_cards_player_gained)
    await add_gains_to_account(
        opponent, new_opponent_morale, money_opponent_gained,
        action_cards_opponent_gained, reaction_cards_opponent_gained)

    # player has no more moves in the current clash
    if moves_table[0] == 0 and moves_table[1] == 0:        
        if opponent.state == PlayerState.AWAIT_CLASH_END:
            new_clash_initiated = consumer.init_table_for_new_clash()
            if not new_clash_initiated: return

            await consumer.send_message_to_group(None, "clash_end")
        else:
            consumer.critical_error(
            f"Improper state {game_user.state} of {game_user.conflict_side} \
            player in clash reaction move.")


async def add_gains_to_account(
        user, new_morale, money_gained, action_cards_gained, reaction_cards_gained):

    await user.set_morale(new_morale)
    await user.add_money(money_gained)
    
    for action_card in action_cards_gained:
        await user.add_action_card(action_card)

    for reaction_card_data in reaction_cards_gained:
        await user.add_reaction_card(
            reaction_card_data.get("reaction_card_id"),
            reaction_card_data.get("amount"))