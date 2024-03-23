from uuid import uuid4
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Card(models.Model):
    pass # TODO: Implement abstraction later

class ActionCard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=150)
    playerType_choices = [
        ('Student', 'Student'),
        ('Teacher', 'Teacher')        
    ]
    playerType = models.CharField(max_length=20, choices=playerType_choices)
    price = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    pressure = models.IntegerField()

class ReactionCard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=150)
    values = models.CharField()
    playerType_choices = [
        ('Student', 'Student'),
        ('Teacher', 'Teacher')        
    ]
    playerType = models.CharField(max_length=20, choices=playerType_choices)
    price = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)]
    ) 
    type_choices = [
        ('Brute', 'Brute'),
        ('Influence', 'Influence'),
        ('Intelligence', 'Intelligence')
    ]
    type = models.CharField(max_length=20, choices=type_choices)
