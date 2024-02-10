from django.db import models

class Card(models.Model):
    pass

class ActionCard(Card):
    pass

class ReactionCard(Card):
    pass

class OwnedReactionCard(models.Model):
    reaction_card = models.ForeignKey(ReactionCard, on_delete=models.CASCADE, null=False, blank=False)
    amount = models.PositiveSmallIntegerField(default=0)

class Task(models.Model):
    pass

class StudentTask(Task):
    pass

class TeacherTask(Task):
    pass
