from gameMechanics.enums import GameStage
from gameMechanics.functions import check_game_stage

from gameNetworking.mechanics.enums import MessageType
from gameNetworking.mechanics.queries import *


async def main_game_loop_impl(consumer, data): # responsible for managing current user messages, effectively main game loop function

    if consumer.game_id is not None:    # has game started or not

        message_type = data.get('type')
        game = await get_game(consumer.game_id)
        game_user = await get_game_user_by_id(consumer.game_user_id)
        game_stage = check_game_stage(consumer.moves_table[0])

        consumer.logger.critical(game_stage)

        if game_stage == GameStage.FIRST_COLLECTING or game_stage == GameStage.SECOND_COLLECTING:
            await collecting_stage_impl(consumer, message_type, game_user, game_stage) 
        elif game_stage == GameStage.FIRST_CLASH or game_stage == GameStage.SECOND_CLASH:
            await clash_stage_impl(consumer, message_type, game, game_user, game_stage, data) 
        else:
            if consumer.winner is None:
                consumer.logger.error("Neither game stage is taking place.")
                await consumer.send_message_to_group("Server error occured", "error")
            else:
                await consumer.send_message_to_group(consumer.winner, "game_end")
                consumer.logger.debug("Game has ended.")
    else:
        await consumer.error("The game hasn't started yet.")

async def clash_stage_impl(consumer, message_type, game, game_user, game_stage, data):

    if message_type == MessageType.CLASH_ACTION_MOVE:
        consumer.logger.critical("clash_action_move")
        action_card_id = data.get("action_card")
        await clash_action_move_mechanics(consumer, game, game_user, game_stage, action_card_id)
    elif message_type == MessageType.CLASH_REACTION_MOVE:
        reaction_cards_ids = data.get("reaction_cards")
        await clash_reaction_move_mechanics(consumer, game, game_user, game_stage, reaction_cards_ids)
    elif message_type == MessageType.SURRENDER_MOVE:
        consumer.winner = "student" if game_user.conflict_side == "teacher" else "teacher"
        await consumer.cleanup()
    else:
        await consumer.error("Wrong message type in the current game stage.")
        
async def collecting_stage_impl(consumer, message_type, game_user, game_stage):

    if message_type == MessageType.COLLECTING_MOVE:
        await collecting_move_mechanics(consumer, game_stage)
    elif message_type == MessageType.SURRENDER_MOVE:
        consumer.winner = "student" if game_user.conflict_side == "teacher" else "teacher"
        await consumer.cleanup()
    else:
        await consumer.error("Wrong message type in the current game stage.")
        consumer.logger.debug("Wrong message type")

async def collecting_move_mechanics(consumer, game_stage):

    if (game_stage == GameStage.FIRST_COLLECTING and consumer.moves_table[0][GameStage.FIRST_COLLECTING] > 0) \
    or (game_stage == GameStage.SECOND_COLLECTING and consumer.moves_table[0][GameStage.SECOND_COLLECTING] > 0):   # if the collecting stage is in action
                                                                                                                   # and player has moves left in the stage
        # choice = data.get("choice")

        # TODO get appriopriate cards
        cards = None
        # TODO save these cards' connection with gameuser

        consumer.moves_table[0][game_stage] -= 1

        if consumer.moves_table[0][game_stage] == 0: # block entered when this is last move in the stage
            await consumer.send_json({"type": "collect_action", "cards": cards})
        else:
            # TODO get a new task
            next_task = None
            await consumer.send_json({"type": "collect_action", "cards": cards, "task": next_task})
    else:
        consumer.logger.debug("Too much moves in the game stage.")
        consumer.error("You have no more moves in that stage.")

async def clash_action_move_mechanics(consumer, game, game_user, game_stage, action_card_id):
    consumer.logger.critical(game.next_move_type)
    consumer.logger.critical(game.next_move_player)
    if game.next_move_type != "action":
        await consumer.error("Wrong message type. It is time for reaction.")
        return

    if game.next_move_player != game_user.conflict_side:
        await consumer.error("Not your turn.")
        return
    
    consumer.logger.critical("Passed 2 ifs")
    if (game_stage == GameStage.FIRST_CLASH and consumer.moves_table[0][GameStage.FIRST_CLASH][0] > 0) \
        or (game_stage == GameStage.SECOND_CLASH and consumer.moves_table[0][GameStage.SECOND_CLASH][0] > 0): # if the clash stage is in action
                                                                                                              # and player has moves left in the stage
        is_card_valid = await is_action_card_valid(action_card_id)
        
        if is_card_valid:
            # succesful_removal = await remove_action_card_connection(game_user, action_card_id)
            # if not succesful_removal:
            #     consumer.logger.error("Couldnt delete action cards from user")
            #     consumer.error("Server error occured")
            consumer.logger.critical("Main logic")
            consumer.moves_table[0][game_stage][0] -= 1
            flag = await update_game_turn(consumer.game_id)
            
            if not flag:
                consumer.logger.error("Couldnt update game turn")
                await consumer.send_message_to_group("Server error occured", "error")
            else:
                await consumer.send_message_to_opponent({"action_card":action_card_id}, "opponent_move") 

        else:
            consumer.logger.debug("You used illegal card.")
            await consumer.error("You used illegal card.")
    else:
        consumer.logger.debug("Too much moves in the stage.")
        await consumer.error("You have no more moves in that stage.")


async def is_action_card_valid(action_card_id):

    # action_card_exist = await check_action_card_exist(action_card_id)
    # if not action_card_exist:
    #     await consumer.error("Provided card doesnt exist")
    #     return False
    
    # game_user = await get_game_user_by_id(consumer.game_user_id)
    # action_card_connected = await check_action_card_connected(game_user, action_card_id)
    # if not action_card_connected:
    #     await consumer.error("You do not own this card")
    #     return False
    return True

async def clash_reaction_move_mechanics(consumer, game, game_user, game_stage, reaction_cards_ids):

    if game.next_move_type != "reaction":
        await consumer.error("Wrong message type. It is time for action.")
        return

    if game.next_move_player != game_user.conflict_side:
        await consumer.error("Not your turn.")
        return

    if (game_stage == GameStage.FIRST_CLASH and consumer.moves_table[0][GameStage.FIRST_CLASH][1] > 0) \
        or (game_stage == GameStage.SECOND_CLASH and consumer.moves_table[0][GameStage.SECOND_CLASH][1] > 0): # if the clash stage is in action
                                                                                                              # and player has moves left in the stage
        await are_reaction_cards_valid(reaction_cards_ids)

        # TODO calculate changes in morale

        # succesful_removal = await remove_reaction_cards_connection(game_user, reaction_cards_ids)
        # if not succesful_removal:
        #     consumer.logger.error("Couldnt delete reaction cards from user")
        #     consumer.error("Server error occured")

        student_new_morale, teacher_new_morale = None, None

        consumer.moves_table[0][game_stage][1] -= 1
        flag = await update_game_turn(consumer.game_id)
        if not flag:
            consumer.logger.error("Couldnt update game turn.")
            await consumer.send_message_to_group("Server error occured.","error")

        await send_clash_end_info(consumer, reaction_cards_ids, student_new_morale, teacher_new_morale)
    else:
        consumer.error("You have no more moves in that stage.")
        consumer.logger.debug("No more moves in the stage.")


async def are_reaction_cards_valid(reaction_cards_ids):

    # all_reaction_cards_exist = await check_reaction_cards_exist(reaction_cards_ids)
    # if not all_reaction_cards_exist:
    #     await consumer.error("Some of provided cards dont exist")
    #     return False
    
    # game_user = await get_game_user_by_id(consumer.game_user_id)
    # all_reaction_cards_connected = await check_reaction_cards_connected(game_user, reaction_cards_ids)
    # if not all_reaction_cards_connected:
    #     await consumer.error("You do not own all of used cards")
    #     return False
    return True

async def send_clash_end_info(consumer, reaction_cards_ids, student_new_morale, teacher_new_morale):

    await consumer.send_message_to_opponent({"reaction_cards": reaction_cards_ids}, "opponent_move") # sends info to opponent about used reaction cards
    await consumer.send_message_to_group({ # sends results of clash to both players
        "student_new_morale": student_new_morale,
        "teacher_new_morale": teacher_new_morale,
        }, "clash_result")