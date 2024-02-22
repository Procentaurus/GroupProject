from gameNetworking.enums import GameStage


def init_table_for_new_clash_impl(consumer):

    consumer.__turns_to_incrementation -= 1

    if consumer.__turns_to_incrementation == 0:

        if consumer.__moves_table[0] != 0 or consumer.__moves_table[1] != 0:
            consumer.critical_error(
                "Try to init moves table for the new clash while some \
                moves still available.")
            return False
        
        consumer.__turns_to_incrementation = consumer.__turns_between_incrementations
        if consumer.__action_moves_per_clash < consumer.__max_moves_per_clash:
            consumer.__action_moves_per_clash += 1

    for i in range(2):
        consumer.__moves_table[i] = consumer.__action_moves_per_clash

    return True

def update_game_stage_impl(consumer):
    if consumer.__game_stage == GameStage.HUB:
        consumer.__game_stage = GameStage.CLASH
    else:
        consumer.__game_stage = GameStage.HUB
