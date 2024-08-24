from django.utils import timezone

from .game_archive.game_archive import GameArchive


def create_game_archive(game, winner):
    if game is not None:
        teacher_player = game.teacher_player.user
        student_player = game.student_player.user
        archive = GameArchive.objects.create(
            start_date=game.start_datetime.date(),
            start_time=game.start_datetime.time(),
            winner=winner,
            teacher_player=teacher_player,
            student_player=student_player,
            length_in_sec=(timezone.now() - game.start_datetime).total_seconds()
        )
        archive.save()
