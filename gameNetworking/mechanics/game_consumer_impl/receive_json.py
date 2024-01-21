from gameMechanics.enums import GameStage
from gameMechanics.functions import check_game_stage

from gameNetworking.mechanics.enums import MessageType
from gameNetworking.mechanics.queries import *


async def main_game_loop_impl(consumer, data): # responsible for managing current user messages, effectively main game loop function

    if consumer.get_game_id() is not None:    # has game started or not

        message_type = data.get('type')
        game_id = consumer.get_game_id()
        game_user = await get_game_user(consumer.get_game_user_id())
        game_stage = check_game_stage(consumer.get_moves_table()[0])

        if game_stage == GameStage.FIRST_COLLECTING or game_stage == GameStage.SECOND_COLLECTING:
            await collecting_stage_impl(consumer, game_id, message_type, game_user, game_stage) 
        elif game_stage == GameStage.FIRST_CLASH or game_stage == GameStage.SECOND_CLASH:
            await clash_stage_impl(consumer, message_type, game_id, game_user, game_stage, data) 
        else:
            winner = consumer.get_winner()
            if winner is None:
                consumer.logger.error("Neither game stage is taking place.")
                await consumer.send_message_to_group("Server error occured", "error")
            else:
                await consumer.send_message_to_group(winner, "game_end")
                consumer.logger.debug("Game has ended.")
    else:
        await consumer.error("The game hasn't started yet.")

async def clash_stage_impl(consumer, message_type, game_id, game_user, game_stage, data):

    if message_type == MessageType.CLASH_ACTION_MOVE:
        action_card_id = data.get("action_card")
        await clash_action_move_mechanics(consumer, game, game_user, game_stage, action_card_id)
    elif message_type == MessageType.CLASH_REACTION_MOVE:
        reaction_cards_ids = data.get("reaction_cards")
        await clash_reaction_move_mechanics(consumer, game, game_user, game_stage, reaction_cards_ids)
    elif message_type == MessageType.SURRENDER_MOVE:
        winner = "student" if game_user.conflict_side == "teacher" else "teacher"
        consumer.set_winner(winner)
        await consumer.cleanup()
    else:
        await consumer.error("Wrong message type in the current game stage.")
        
async def collecting_stage_impl(consumer, message_type, game_user, game_stage):

    if message_type == MessageType.COLLECTING_MOVE:
        await collecting_move_mechanics(consumer, game_id, game_stage, game_user)
    elif message_type == MessageType.SURRENDER_MOVE:
        winner = "student" if game_user.conflict_side == "teacher" else "teacher"
        consumer.set_winner(winner)
        await consumer.cleanup()
    else:
        await consumer.error("Wrong message type in the current game stage.")
        consumer.logger.debug("Wrong message type")

async def collecting_move_mechanics(consumer, game_stage):

    moves_table = consumer.get_moves_table()
    
    if (game_stage == GameStage.FIRST_COLLECTING and moves_table[0][GameStage.FIRST_COLLECTING] > 0) \
    or (game_stage == GameStage.SECOND_COLLECTING and moves_table[0][GameStage.SECOND_COLLECTING] > 0):   # if the collecting stage is in action
                                                                                                          # and player has moves left in the stage
        # choice = data.get("choice")

        # TODO get appriopriate cards
        cards = None
        # TODO save these cards' connection with gameuser

        moves_table[0][game_stage] -= 1

        if moves_table[0][game_stage] == 0: # block entered when this is last move in the stage
            await consumer.send_json({"type": "collect_action", "cards": cards})
        else:
            # TODO get a new task
            next_task = None
            await consumer.send_json({"type": "collect_action", "cards": cards, "task": next_task})
    else:
        consumer.logger.debug("Too much moves in the game stage.")
        consumer.error("You have no more moves in that stage.")

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
            
            moves_table[0][game_stage][0] -= 1
            flag = await update_game_turn(consumer.get_game_id())
            
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


async def is_action_card_valid(consumer, game_user, action_card_id):

    # action_card_exist = await check_action_card_exist(action_card_id)
    # if not action_card_exist:
    #     await consumer.error("Provided card doesnt exist")
    #     return False
    
    # action_card_owned = await game_user.check_if_own_action_card(action_card_id)
    # if not action_card_owned:
    #     await consumer.error("You do not own this card")
    #     return False
    return True

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

        await send_clash_end_info(consumer, reaction_cards_ids, student_new_morale, teacher_new_morale)
    else:
        await consumer.error("You have no more moves in that stage.")
        consumer.logger.debug("No more moves in the stage.")


async def are_reaction_cards_valid(consumer, game_user, reaction_cards_ids):

    # all_reaction_cards_exist = await check_reaction_cards_exist(reaction_cards_ids)
    # if not all_reaction_cards_exist:
    #     await consumer.error("Some of provided cards dont exist")
    #     return False
    
    # all_reaction_cards_owned = True
    # for reaction_card_id in reaction_cards_ids:
    #     all_reaction_cards_owned = all_reaction_cards_owned and await game_user.check_if_own_reaction_card(reaction_card_id)

    # if not all_reaction_cards_owned:
    #     await consumer.error("You do not own all of used reaction cards")
    #     return False
    return True

async def send_clash_result_info(consumer, reaction_cards_ids, student_new_morale, teacher_new_morale):
    await consumer.send_message_to_opponent({"reaction_cards": reaction_cards_ids}, "opponent_move") # sends info to opponent about used reaction cards
    await consumer.send_message_to_group({ # sends results of clash to both players
        "student_new_morale": student_new_morale,
        "teacher_new_morale": teacher_new_morale,
    }, "clash_result")  