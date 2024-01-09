from django.db import models

class Entity(models.Model):
    name = models.CharField(max_length=15)
    description = models.CharField(max_length=100)

class ActionCard(Entity):
    damage_value = models.IntegerField()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = 'Insult'
        self.description = 'Insult your oponent for 20 damage.'
        self.damage_value = 20

class ReactionCard(Entity):
    defense_value = models.IntegerField()
    type_choices = [
        'Brute',
        'Influence',
        'Inteligence'
    ]
    type = models.CharField(max_length=15, choices=type_choices)

class Task(Entity):
    arena_choices = [
         'Hallway',
         'Classroom',
         'Canteen'
    ]
    arena = models.CharField(max_length=15, choices=arena_choices)

class StudentTask(Task):
    pass

class TeacherTask(Task):
    pass
