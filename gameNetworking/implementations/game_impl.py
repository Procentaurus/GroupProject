from channels.db import database_sync_to_async


@database_sync_to_async
def get_opponent_player_impl(game, game_user):
    if game_user.id == game.student_player.id:
        return game.teacher_player
    else:
        return game.student_player
