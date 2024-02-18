from django.db import models

class Card(models.Model):
    price = models.PositiveIntegerField(default=0)
    pass

class ActionCard(Card):
    pass

class ReactionCard(Card):
    pass
