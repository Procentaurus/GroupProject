async def surrender_move_mechanics(consumer, game_user):
    consumer.logger.info(f"{game_user.conflict_side} player has surrendered.")

    winner = "student" if game_user.conflict_side == "teacher" else "teacher"
    consumer.set_closure_from_user_side(False)
    await consumer.send_message_to_group(
        {"winner" : winner, "after_surrender" : True},
        "game_end")
