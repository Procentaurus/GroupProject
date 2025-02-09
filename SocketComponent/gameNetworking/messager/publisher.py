import redis
import json
from django.utils import timezone
from django.conf import settings

from SocketComponent.loggers import get_server_logger


redis_client = redis.StrictRedis(
    host=settings.REDIS_MESSAGING_HOST,
    port=settings.REDIS_MESSAGING_PORT,
    db=settings.REDIS_MESSAGING_DB
)

logger = get_server_logger()


def clear_in_game_status(user_id):
    redis_client.publish(
        settings.IN_GAME_STATUS_MESSAGING_CHANNEL_NAME,
        json.dumps({
            'user_id': user_id,
            'new_status': False
        })
    )
    logger.info(f"User({user_id}) published 'in game' status clear request")

def set_in_game_status(user_id):
    redis_client.publish(
        settings.IN_GAME_STATUS_MESSAGING_CHANNEL_NAME,
        json.dumps({
            'user_id': user_id,
            'new_status': True
        })
    )
    logger.info(f"User({user_id}) published 'in game' status set request")

async def create_archive(game, winner):
    teacher = await game.get_teacher_player()
    student = await game.get_student_player()
    redis_client.publish(
        settings.ARCHIVE_CREATION_MESSAGING_CHANNEL_NAME,
        json.dumps({
            'winner': winner,
            'teacher_id': str(teacher.user_id),
            'student_id': str(student.user_id),
            'len_in_sec': (timezone.now() - game.start_datetime).total_seconds(),
            'start_datetime': game.start_datetime.isoformat(),
        })
    )
    logger.info(f"Game({game.id})'s 'arcvhive creation' request published")
