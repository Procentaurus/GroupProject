from enum import IntEnum

class GameStage(IntEnum):
    FIRST_COLLECTING = 0
    FIRST_CLASH = 1
    SECOND_COLLECTING = 2
    SECOND_CLASH = 3


def check_game_stage(game_iteration):
       
    if game_iteration[0] > 0:
        return GameStage.FIRST_COLLECTING
    elif game_iteration[0] == 0 and (game_iteration[1][0] > 0 or game_iteration[1][1] > 0):
        return GameStage.FIRST_CLASH
    elif game_iteration[0] == 0 and (game_iteration[1][0] == 0 and game_iteration[1][1] == 0) and game_iteration[2] > 0:
        return GameStage.SECOND_COLLECTING
    elif game_iteration[0] == 0 and (game_iteration[1][0] == 0 and game_iteration[1][1] == 0) and game_iteration[2] == 0 and (game_iteration[3][0] > 0 or game_iteration[3][1] > 0):
        return GameStage.SECOND_CLASH
    