from gameMechanics.enums import GameStage


def init_table_for_new_clash_impl(consumer):
    if consumer.__moves_table[0] != 0 or consumer.__moves_table[1] != 0:
        return False
    
    for i in range(2):
        consumer.__moves_table[i] = 1 * consumer.__action_multiplier
    return True

def update_action_multiplier_impl(consumer):
    if consumer.__action_multiplier < 3:
        consumer.__action_multiplier += 1

def update_game_stage_impl(consumer):
    if consumer.__game_stage == GameStage.HUB:
        consumer.__game_stage = GameStage.CLASH
    else:
        consumer.__game_stage = GameStage.HUB