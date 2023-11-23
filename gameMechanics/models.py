from django.db import models

class Card(models.Model):
    pass

class ActionCard(Card):
    pass

class ReactionCard(Card):
    pass

class Choice(models.Model):
    pass

class StudentChoice(Choice):
    pass

class TeacherModel(Choice):
    pass

class Task(models.Model):
    pass

class StudentTask(Task):
    pass

class TeacherTask(Task):
    pass
