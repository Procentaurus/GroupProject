from uuid import uuid4
from django.db import models

from gameMechanics.models import ReactionCard

from ..game_user.game_user import GameUser


class ReactionCardInShop(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    reaction_card = models.ForeignKey(
        ReactionCard, on_delete=models.CASCADE, null=False, blank=False)
    game_user = models.ForeignKey(
        GameUser, on_delete=models.CASCADE, null=False, blank=False)
    amount = models.PositiveSmallIntegerField(default=0)
