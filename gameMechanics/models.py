from django.db import models

class Card(models.Model):
    price = models.PositiveIntegerField(null=False, blank=False)
    pass

class ActionCard(Card):
    pass

class ReactionCard(Card):
    pass
