from channels.db import database_sync_to_async


@database_sync_to_async
def get_opponent_player_impl(game, game_user):
    if game_user.id == game.student_player.id:
        return game.teacher_player
    else:
        return game.student_player

@database_sync_to_async  
def update_after_turn_impl(game):
    current_move_player = game.next_move_player
    current_move_type = game.next_move_type

    if current_move_type == "action":
        game.next_move_type = "reaction"
        if current_move_player == "student":
            game.next_move_player = "teacher"
        else:
            game.next_move_player = "student"
    else:
        game.next_move_type = "action"

    game.save()
    return True
