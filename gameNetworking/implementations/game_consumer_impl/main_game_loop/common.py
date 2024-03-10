from gameMechanics.scripts.initial_shop import get_initial_shop_for_player


async def send_card_sets_to_shop(consumer, is_current_game_user_teacher):

    initial_reaction_cards_for_teacher, initial_action_cards_for_teacher = (
        get_initial_shop_for_player(5, 2, "teacher")
    )
    initial_reaction_cards_for_student, initial_action_cards_for_student = (
        get_initial_shop_for_player(5, 2, "student")
    )

    if is_current_game_user_teacher:
        await send_cards_to_player(consumer, initial_action_cards_for_teacher,
            initial_reaction_cards_for_teacher)
        await send_cards_to_opponent(consumer, initial_action_cards_for_student,
            initial_reaction_cards_for_student)
    else:
        await send_cards_to_player(consumer, initial_action_cards_for_student,
            initial_reaction_cards_for_student)
        await send_cards_to_opponent(consumer, initial_action_cards_for_teacher,
            initial_reaction_cards_for_teacher)

async def surrender_move_mechanics(consumer):
    game_user = consumer.get_game_user()
    consumer.logger.info(f"{game_user.conflict_side} player has surrendered.")

    winner = "student" if game_user.conflict_side == "teacher" else "teacher"
    consumer.set_winner(winner)
    consumer.set_closure_from_user_side(False)
    await consumer.send_message_to_group(
        {"winner" : winner, "after_surrender" : True},
        "game_end")

async def send_cards_to_opponent(consumer, action_cards, reaction_cards):
    await consumer.send_message_to_opponent(
        {"action_cards" : action_cards,
        "reaction_cards" : reaction_cards},
        "card_package")
    
async def send_cards_to_player(consumer, action_cards, reaction_cards):
    await consumer.card_package(
        {"action_cards" : action_cards,
        "reaction_cards" : reaction_cards})
    

async def inform_about_improper_state_error(consumer, move_type):
    game_user = consumer.get_game_user()

    await consumer.critical_error(
        f"Improper state: {game_user.state} of {game_user.conflict_side}"
        + f" player in {move_type}.")
