from uuid import uuid4
from django.db import models

from customUser.models import MyUser

CONFLICT_SIDES = (
        ("teacher", "teacher"),
        ("student", "student"),
    )

class GameUser(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user_id = models.OneToOneField(MyUser, on_delete=models.CASCADE, null=False)
    conflict_side = models.CharField(choices=CONFLICT_SIDES, null=False)
    started_waiting = models.DateTimeField(auto_now_add=True)
    channel_name = models.CharField(null=False)
    in_game = models.BooleanField(default=False)

    class Meta:
        ordering = ["started_waiting"]

class Game(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    teacher_player = models.ForeignKey(GameUser, on_delete=models.SET_NULL)
    student_player = models.ForeignKey(GameUser, on_delete=models.SET_NULL)
    start_datetime = models.DateTimeField(auto_now_add=True)
    end_datetime = models.DateTimeField()
    next_move = models.CharField(choices=CONFLICT_SIDES, null=False)

class GameAuthenticationToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user_id = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=False)
    issued = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-issued"]