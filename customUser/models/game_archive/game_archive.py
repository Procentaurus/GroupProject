from uuid import uuid4
from django.db import models
from django.db import transaction

from ..my_user.my_user import MyUser


CONFLICT_SIDES = (
    ("teacher", "teacher"),
    ("student", "student"),
)

class GameArchive(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    start_date = models.DateField(blank=False)
    start_time = models.TimeField(blank=False)
    lenght_in_sec = models.PositiveIntegerField(null=False, blank=False)
    teacher_player = models.ForeignKey(MyUser, related_name="teacher_player",
        on_delete=models.SET_NULL, null=True)
    student_player = models.ForeignKey(MyUser, related_name="student_player",
        on_delete=models.SET_NULL, null=True)
    winner = models.CharField(choices=CONFLICT_SIDES, null=False, max_length=15)

    class Meta:
        ordering = ["-start_date", "-start_time"]

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        with transaction.atomic():
            super().save(*args, **kwargs)
            if is_new:
                self.inc_players_stats()

    def inc_players_stats(self):
        self.teacher_player.inc_games_played()
        self.student_player.inc_games_played()
        if self.winner == "teacher":
            self.teacher_player.inc_games_won()
        else:
            self.student_player.inc_games_won()

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            self.dec_players_stats()
            super().delete(*args, **kwargs)

    def dec_players_stats(sender, self, **kwargs):
        self.teacher_player.dec_games_played()
        self.student_player.dec_games_played()
        if self.winner == "teacher":
            self.teacher_player.dec_games_won()
        else:
            self.student_player.dec_games_won()
