from gameMechanics.scripts.initial_shop import get_initial_shop_for_player


async def send_card_sets_to_shop(consumer, is_current_game_user_teacher):

    # TODO alter the names
    initial_action_cards_for_teacher, initial_reaction_cards_for_teacher = (
        await get_initial_shop_for_player(5, 2, "teacher")
    )
    initial_action_cards_for_student, initial_reaction_cards_for_student = (
        await get_initial_shop_for_player(5, 2, "student")
    )

    # sending initial sets of cards to players
    if is_current_game_user_teacher:
        await consumer.card_package(
            {"action_cards" : initial_action_cards_for_teacher,
            "reaction_cards" : initial_reaction_cards_for_teacher})
        await consumer.send_message_to_opponent(
            {"action_cards" : initial_action_cards_for_student,
            "reaction_cards" : initial_reaction_cards_for_student},
            "card_package")
    else:
        await consumer.card_package(
            {"action_cards" : initial_action_cards_for_student,
            "reaction_cards" : initial_reaction_cards_for_student})
        await consumer.send_message_to_opponent(
            {"action_cards" : initial_action_cards_for_teacher,
            "reaction_cards" : initial_reaction_cards_for_teacher},
            "card_package")

async def surrender_move_mechanics(consumer):
    game_user = consumer.get_game_user()
    consumer.logger.info(f"{game_user.conflict_side} player has surrendered.")

    winner = "student" if game_user.conflict_side == "teacher" else "teacher"
    consumer.set_winner(winner)
    consumer.set_closure_from_user_side(False)
    await consumer.send_message_to_group(
        {"winner" : winner, "after_surrender" : True},
        "game_end")
