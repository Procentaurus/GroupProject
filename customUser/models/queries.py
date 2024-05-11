import datetime

from .game_archive.game_archive import GameArchive


### game_archive ###

def create_game_archive(game, winner):
    archive = GameArchive.objects.create(
        start_date=game.start_datetime.date(),
        start_time=game.start_datetime.time(),
        winner=winner,
        teacher_player=game.teacher_player.user,
        student_player=game.student_player.user,
        length_in_sec = (datetime.now() - game.start_datetime).total_seconds()
    )
    archive.save()
    return archive