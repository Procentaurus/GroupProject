from gameMechanics.enums import GameStage


def check_game_stage(game_iteration): # check game stage by checking moves_table defined for each player in GameConsumer
       
    if game_iteration[0] > 0:
        return GameStage.FIRST_COLLECTING
    elif game_iteration[0] == 0 and (game_iteration[1][0] > 0 or game_iteration[1][1] > 0):
        return GameStage.FIRST_CLASH
    elif game_iteration[0] == 0 and (game_iteration[1][0] == 0 and game_iteration[1][1] == 0) and game_iteration[2] > 0:
        return GameStage.SECOND_COLLECTING
    elif game_iteration[0] == 0 and (game_iteration[1][0] == 0 and game_iteration[1][1] == 0) and game_iteration[2] == 0 and (game_iteration[3][0] > 0 or game_iteration[3][1] > 0):
        return GameStage.SECOND_CLASH