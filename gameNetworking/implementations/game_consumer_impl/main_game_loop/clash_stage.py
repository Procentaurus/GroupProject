from gameMechanics.enums import PlayerState

from gameNetworking.enums import MessageType
from gameNetworking.queries import get_game, update_game_turn
from .surrender import surrender_move_mechanics
from .checkers import *

async def clash_stage_impl(consumer, game, game_stage, message_type, game_user, data):

    if message_type == MessageType.CLASH_ACTION_MOVE:
        action_card_id = data.get("action_card")
        await clash_action_move_mechanics(consumer, game, game_user, action_card_id)
    elif message_type == MessageType.CLASH_REACTION_MOVE:
        reaction_cards_data = data.get("reaction_cards")
        await clash_reaction_move_mechanics(
            consumer, game, game_user, reaction_cards_data)
    elif message_type == MessageType.SURRENDER_MOVE:
        await surrender_move_mechanics(consumer, game_user)
    else:
        await consumer.error(
            f"Wrong message type in the {game_stage} game stage.")

async def clash_action_move_mechanics(consumer, game, game_user, action_card_id):

    action_move_can_be_performed = await check_action_move_can_be_performed(
        consumer, game, game_user, action_card_id)
    if not action_move_can_be_performed: return
    
    action_card_exist = await check_all_action_cards_exist(consumer, [action_card_id])
    if not action_card_exist: return

    action_card_is_owned = await check_game_user_own_action_card(
        consumer, game_user, action_card_id)
    if not action_card_is_owned: return

    moves_table = consumer.get_moves_table()
    moves_table[0] -= 1 # 0 is index of action moves

    updated_game_turn = await update_game_turn(game)
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
        consumer, game, game_user, reaction_cards_data):
    
    reaction_move_can_be_performed = await check_reaction_move_can_be_performed(
        consumer, game, game_user, reaction_cards_data)
    if not reaction_move_can_be_performed: return

    updated_game_turn = await update_game_turn(game)
    if not updated_game_turn:
        await consumer.critical_error("Updating game turn impossible.")
        return

    moves_table = consumer.get_moves_table()
    moves_table[1] -= 1 # 1 is index of reaction moves

    #TODO call functions that return needed values
    new_player_morale, new_opponent_morale = None, None
    money_player_gained, money_opponent_gained = None, None
    action_cards_player_gained, action_cards_opponent_gained = None, None
    reaction_cards_player_gained, reaction_cards_opponent_gained = None, None

    await consumer.send_message_to_opponent(
        {"reaction_cards" : reaction_cards_data},
        "opponent_move")
    
    there_is_winner = await check_winner(
        consumer, game_user, opponent, new_player_morale, new_opponent_morale)
    if there_is_winner: return

    game_user_message_body = await create_clash_result_response_body(
        new_player_morale,  new_opponent_morale, money_player_gained,
        action_cards_player_gained, reaction_cards_player_gained)
    await consumer.clash_result(game_user_message_body)

    opponent_message_body = await create_clash_result_response_body(
        new_opponent_morale,  new_player_morale, money_opponent_gained,
        action_cards_opponent_gained, reaction_cards_opponent_gained)
    await consumer.send_message_to_opponent(opponent_message_body,"clash_result")

    opponent = await game.get_opponent_player(game_user.id)
    await add_gains_to_account(
        game_user, new_player_morale, money_player_gained,
        action_cards_player_gained, reaction_cards_player_gained)
    await add_gains_to_account(
        opponent, new_opponent_morale, money_opponent_gained,
        action_cards_opponent_gained, reaction_cards_opponent_gained)
    
    await remove_all_used_reaction_cards(game_user, reaction_cards_data)

    # player has no more moves in the current clash
    if moves_table[0] == 0 and moves_table[1] == 0:        
        if opponent.state == PlayerState.AWAIT_CLASH_END:
            new_clash_initiated = consumer.init_table_for_new_clash()
            if not new_clash_initiated: return

            await consumer.send_message_to_group({}, "clash_end")
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

async def create_clash_result_response_body(new_morale, new_opponent_morale, money_gained, action_cards_gained, reaction_cards_gained):
    return {
        "new_player_morale" : new_morale,
        "new_opponent_morale" : new_opponent_morale,
        "money_gained" : money_gained,
        "action_cards_gained" : action_cards_gained,
        "reaction_cards_gained" : reaction_cards_gained
    }

async def remove_all_used_reaction_cards(game_user, reaction_cards_data):
    for reaction_card_data in reaction_cards_data:
        await game_user.remove_reaction_card(game_user,
            reaction_card_data.get("reaction_card_id"),
            reaction_card_data.get("amount"))
