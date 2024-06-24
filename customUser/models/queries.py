from django.utils import timezone
from channels.db import database_sync_to_async

from .game_archive.game_archive import GameArchive


### game_archive ###

@database_sync_to_async
def create_archive(game, winner, teacher_player, student_player):
    archive = GameArchive.objects.create(
        start_date=game.start_datetime.date(),
        start_time=game.start_datetime.time(),
        winner=winner,
        teacher_player=teacher_player,
        student_player=student_player,
        length_in_sec=(timezone.now() - game.start_datetime).total_seconds()
    )
    archive.save()
    return archive

async def create_game_archive(game, winner):
    teacher_player = await (await game.get_teacher_player()).get_user()
    student_player = await (await game.get_student_player()).get_user()
    archive = await create_archive(game, winner, teacher_player, student_player)
    return archive
