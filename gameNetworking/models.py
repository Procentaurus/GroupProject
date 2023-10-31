from uuid import uuid4
from django.db import models

from customUser.models import MyUser


class Game(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    teacher_player = models.ForeignKey(MyUser, on_delete=models.SET_NULL)
    student_player = models.ForeignKey(MyUser, on_delete=models.SET_NULL)
    start_datetime = models.DateTimeField(auto_now_add=True)
    end_datetime = models.DateTimeField()

class GameWaitingUser(models.Model):

    CONFLICT_SIDES = (
        ("Teacher", "Teacher"),
        ("Student", "Student"),
    )

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user_id = models.OneToOneField(MyUser, on_delete=models.SET_NULL)
    conflict_side = models.CharField(choices=CONFLICT_SIDES)
    # level = models.SmallIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(3)])

class GameAuthenticatedUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user_id = models.OneToOneField(MyUser, on_delete=models.SET_NULL)


class GameAuthenticationToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user_id = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    issued = models.DateTimeField(auto_now_add=True)