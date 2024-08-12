from uuid import uuid4
from django.db import models
from channels.db import database_sync_to_async


class GameAuthenticationToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user_id = models.UUIDField(
        primary_key=True, default=uuid4, editable=False, unique=True)
    issued = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-issued"]

    #################################  Getters  ################################
    def get_user_id(self):
        return self.user_id
