from uuid import uuid4
from django.db import models

from customUser.models import MyUser
from gameMechanics.models import *

#
# Implementation of all entity classes crucial for the module
#

CONFLICT_SIDES = (
    ("teacher", "teacher"),
    ("student", "student"),
)
MOVE_TYPES = (
    ("action", "action"),
    ("reaction", "reaction")
)

class GameUser(models.Model): # user has new instance of GameUser created for every new game

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE, null=False)

    started_waiting = models.DateTimeField(auto_now_add=True)
    channel_name = models.CharField(null=False, max_length=100)
    in_game = models.BooleanField(default=False)

    morale = models.SmallIntegerField(default=100, null=False, blank=False)
    conflict_side = models.CharField(choices=CONFLICT_SIDES, null=False, max_length=15)
    # action_cards = models.ManyToManyField(ActionCard, null=True)
    # reaction_cards = models.ManyToManyField(ReactionCard, null=True)

    class Meta:
        ordering = ["started_waiting"]

class Game(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    teacher_player = models.ForeignKey(GameUser, related_name="teacher_player", on_delete=models.SET_NULL, null=True)
    student_player = models.ForeignKey(GameUser, related_name="student_player", on_delete=models.SET_NULL, null=True)
    start_datetime = models.DateTimeField(auto_now_add=True)
    end_datetime = models.DateTimeField(null=True, blank=True)
    next_move_player = models.CharField(choices=CONFLICT_SIDES, max_length=15, null=False)
    next_move_type = models.CharField(choices=MOVE_TYPES, max_length=15, null=False, default="action")

class GameAuthenticationToken(models.Model):  # entity class of single-use tokens needed to authenticate to websocket
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=False)
    issued = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-issued"]