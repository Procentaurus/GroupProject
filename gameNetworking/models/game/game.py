
from uuid import uuid4
from django.db import models
from channels.db import database_sync_to_async

from ..common import CONFLICT_SIDES, MOVE_TYPES
from ..game_user.game_user import GameUser
from .methods import *


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

    turns_to_inc = models.PositiveSmallIntegerField(default=0)
    moves_per_clash = models.PositiveSmallIntegerField(default=0)
    stage = models.BooleanField(default=False)
    is_backuped = models.BooleanField(default=False)
    delayed_tasks = models.JSONField(default=dict)

    #################################  Getters  ################################
    @database_sync_to_async
    def get_teacher_player(self):
        return self.teacher_player

    @database_sync_to_async
    def get_student_player(self):
        return self.student_player

    #################################  Setters  ################################
    @database_sync_to_async
    def clear_backup_status(self):
        self.is_backuped = False
        self.save()

    #######################  State changing functions  #########################
    @database_sync_to_async
    def update_after_turn(self):
        pass

    @database_sync_to_async
    def get_opponent_player(self, game_user):
        pass

    @database_sync_to_async
    def backup(self, consumer):
        pass

    def delete(self, *args, **kwargs):
        if self.teacher_player:
            self.teacher_player.delete()
        if self.student_player:
            self.student_player.delete()
        super().delete(*args, **kwargs)

Game.backup = backup
Game.update_after_turn = update_after_turn
Game.get_opponent_player = get_opponent_player
