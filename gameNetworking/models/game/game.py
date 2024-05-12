
from uuid import uuid4
from django.db import models
from channels.db import database_sync_to_async

from ..common import CONFLICT_SIDES, MOVE_TYPES
from ..game_user.game_user import GameUser
from .methods_impl import *


class Game(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    start_datetime = models.DateTimeField(auto_now_add=True)

    teacher_player = models.OneToOneField(GameUser,
        related_name="teacher_player", on_delete=models.CASCADE, null=True)
    student_player = models.OneToOneField(GameUser,
        related_name="student_player", on_delete=models.CASCADE, null=True)

    next_move_player = models.CharField(
        choices=CONFLICT_SIDES, max_length=15, null=False)
    next_move_type = models.CharField(
        choices=MOVE_TYPES, max_length=15, null=False, default="action")

    @database_sync_to_async
    def get_teacher_player(self):
        return self.teacher_player
        
    @database_sync_to_async
    def get_student_player(self):
        return self.student_player
    
    @database_sync_to_async
    def update_after_turn(self):
        result = update_after_turn_impl(self)
        return result
    
    @database_sync_to_async
    def get_opponent_player(self, game_user):
        result = get_opponent_player_impl(self, game_user)
        return result
