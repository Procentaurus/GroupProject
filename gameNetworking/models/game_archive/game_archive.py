from uuid import uuid4
from django.db import models

from customUser.models import MyUser

from ..common import CONFLICT_SIDES


class GameArchive(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    start_datetime = models.DateTimeField(auto_now_add=True)
    end_datetime = models.DateTimeField(null=True, blank=True)

    teacher_player = models.OneToOneField(MyUser, related_name="teacher_player",
        on_delete=models.SET_NULL, null=True)
    student_player = models.OneToOneField(MyUser, related_name="student_player",
        on_delete=models.SET_NULL, null=True)
    winner = models.CharField(choices=CONFLICT_SIDES, null=False, max_length=15)

    class Meta:
        ordering = ["start_datetime"]
