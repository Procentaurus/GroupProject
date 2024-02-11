from gameMechanics.enums import PlayerState, GameStage

from gameNetworking.implementations.game_consumer_impl.purchasing import *
from gameNetworking.enums import MessageType
from gameNetworking.queries import *

# main game loop function responsible for taking care of user requests to socket
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
        await consumer.perform_error_handling(
            f"{game_user.conflict_side} made move before the game has started")

async def clash_stage_impl(consumer, message_type, game_id, game_user, data):

    if message_type == MessageType.CLASH_ACTION_MOVE:
        action_card_id = data.get("action_card")
        await clash_action_move_mechanics(consumer, game_id, game_user, action_card_id)
    elif message_type == MessageType.CLASH_REACTION_MOVE:
        reaction_cards_ids = data.get("reaction_cards")
        await clash_reaction_move_mechanics(consumer, game_id, game_user, reaction_cards_ids)
    elif message_type == MessageType.SURRENDER_MOVE:
        await surrender_move_mechanics(consumer, game_user)
    else:
        await consumer.perform_error_handling(
            f"Wrong message type in the {consumer.get_game_stage()} game stage.")
        
async def hub_stage_impl(consumer, game_id, message_type, game_user, data):

    if message_type == MessageType.PURCHASE_MOVE:
        await purchase_move_mechanics(consumer, game_user, data)
    elif message_type == MessageType.READY_MOVE:
        await ready_move_mechanics(consumer, game_id, game_user, data)
    elif message_type == MessageType.SURRENDER_MOVE:
        await surrender_move_mechanics(consumer, game_user)
    else:
        await consumer.perform_error_handling(
            f"Wrong message type in the {consumer.get_game_stage()} game stage.")

async def surrender_move_mechanics(consumer, game_user):
    consumer.logger.info(f"{game_user.conflict_side} has surrendered.")

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
        await consumer.perform_error_handling_impl(
            consumer, "You have already declared readyness.",
            f"{game_user.conflict_side} tried to declare readiness \
            for the clash afresh.")
        return
    
    # Check if player is in the hub stage, if not then flow error occured
    if game_user.state != PlayerState.IN_HUB:
        await consumer.perform_critical_error_handling_impl(consumer,
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
        await consumer.perform_critical_error_handling(
            f"Improper opponent player state: {opponent.state}")

async def purchase_move_mechanics(consumer, game_user, data):

    # Check if player is in the state after reporting readiness 
    if game_user.state == PlayerState.AWAIT_CLASH_START:
        await consumer.perform_error_handling_impl(
            consumer, "You cannot purchase cards after declaring readiness for clash.",
            f"{game_user.conflict_side} tried to purchase cards after declaring readiness.")
        return
    
    # Check if player is in the hub stage, if not then flow error occured
    if game_user.state != PlayerState.IN_HUB:
        await consumer.perform_critical_error_handling_impl(consumer,
            f"Improper state {game_user.state} of {game_user.conflict_side} \
            player in purchase_move.")
        return

    action_cards_ids = data.get("action_cards")
    reaction_cards_data = data.get("reaction_cards")
    reaction_cards_ids = {x.get("reaction_card_id") for x in reaction_cards_data}

    all_cards_exist = await check_all_cards_exist(
        consumer, action_cards_ids, reaction_cards_ids)
    if not all_cards_exist: return

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
            consumer, game_user, reaction_card_data["reaction_card_id"],
            reaction_card_data["amount"])
        
    await consumer.purchase_result({"new_money_amount" : game_user.money})

async def clash_action_move_mechanics(consumer, game_id, game_user, game_stage, action_card_id):

    game = await get_game(game_id)
    if game.next_move_type != "action":
        await consumer.error("Wrong message type. It is time for reaction.")
        return

    if game.next_move_player != game_user.conflict_side:
        await consumer.error("Not your turn.")
        return
    
    moves_table = consumer.get_moves_table()
    
    if (game_stage == GameStage.FIRST_CLASH and moves_table[0][GameStage.FIRST_CLASH][0] > 0) \
        or (game_stage == GameStage.SECOND_CLASH and moves_table[0][GameStage.SECOND_CLASH][0] > 0): # if the clash stage is in action
                                                                                                     # and player has moves left in the stage
        is_card_valid = await is_action_card_valid(consumer, game_user, action_card_id)
        
        if is_card_valid:
            # succesful_removal = await remove_action_card_connection(game_user, action_card_id)
            # if not succesful_removal:
            #     consumer.logger.error("Couldnt delete action cards from user")
            #     consumer.error("Server error occured")
            #     consumer.close()
            
            moves_table[0][game_stage][0] -= 1
            flag = await update_game_turn(consumer.get_game_id())
            
            if not flag:
                consumer.logger.error("Couldnt update game turn")
                await consumer.send_message_to_group("Server error occured", "error")
                consumer.close()
            else:
                await consumer.send_message_to_opponent({"action_card" : action_card_id}, "opponent_move")
                if moves_table[0][game_stage][0] == 0 and moves_table[0][game_stage][1] == 0: # player has no more moves in the current clash
                    await game_user.set_state(PlayerState.AWAIT_CLASH_END)
        else:
            consumer.logger.debug("You used illegal card.")
            await consumer.error("You used illegal card.")
    else:
        consumer.logger.debug("Too much moves in the stage.")
        await consumer.error("You have no more moves in that stage.")

async def clash_reaction_move_mechanics(consumer, game_id, game_user, game_stage, reaction_cards_ids):

    game = await get_game(game_id)
    if game.next_move_type != "reaction":
        await consumer.error("Wrong message type. It is time for action.")
        return

    if game.next_move_player != game_user.conflict_side:
        await consumer.error("Not your turn.")
        return
    
    moves_table = consumer.get_moves_table()

    if (game_stage == GameStage.FIRST_CLASH and moves_table[0][GameStage.FIRST_CLASH][1] > 0) \
        or (game_stage == GameStage.SECOND_CLASH and moves_table[0][GameStage.SECOND_CLASH][1] > 0): # if the clash stage is in action
                                                                                                              # and player has moves left in the stage
        await are_reaction_cards_valid(consumer, game_user, reaction_cards_ids)

        # TODO calculate changes in morale

        # for reaction_card_id in reaction_cards_ids:
        #     result = game_user.remove_action_card(reaction_card_id)
        #     if result == False:
        #         consumer.logger.error(f"Couldnt delete reaction card of id {reaction_card_id} from user.")
        #         consumer.error("Server error occured")
        #         consumer.close()

        student_new_morale, teacher_new_morale = None, None

        moves_table[0][game_stage][1] -= 1
        flag = await update_game_turn(game.id)
        if not flag:
            consumer.logger.error("Couldnt update game turn.")
            await consumer.send_message_to_group("Server error occured.","error")
            consumer.close()

        await send_clash_result_info(consumer, reaction_cards_ids, student_new_morale, teacher_new_morale)

        opponent = await game.get_opponent_player(game_user.id)
        
        if opponent.state == PlayerState.AWAIT_CLASH_END:
            await consumer.send_message_to_group(None, "clash_end")
        elif opponent.state != PlayerState.IN_CLASH:
            consumer.logger.error("Improper player state.")
            await consumer.error("Server error occured.")
            consumer.close()

    else:
        await consumer.error("You have no more moves in that stage.")
        consumer.logger.debug("No more moves in the stage.")

async def send_clash_result_info(consumer, reaction_cards_ids, student_new_morale, teacher_new_morale):

    await consumer.send_message_to_opponent({"reaction_cards": reaction_cards_ids}, "opponent_move") # sends info to opponent about used reaction cards
    await consumer.send_message_to_group({ # sends results of clash to both players
        "student_new_morale": student_new_morale,
        "teacher_new_morale": teacher_new_morale,
    }, "clash_result") 

    #     game = await get_game(game_id)
    # opponent = await game.get_opponent_player(game_user.id)

    # if opponent.state == PlayerState.IN_HUB:
    #     await game_user.set_state(PlayerState.AWAIT_CLASH_START)
    # elif opponent.state == PlayerState.AWAIT_CLASH_START:
    #     await consumer.send_message_to_group({"next_move_player" : game.next_move_player}, "clash_start")
    # else: