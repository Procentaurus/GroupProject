from uuid import uuid4
from django.db import models
from channels.db import database_sync_to_async

from customUser.models import MyUser


class GameAuthenticationToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=False)
    issued = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-issued"]

    @database_sync_to_async
    def get_game_user(self):
        return self.user
