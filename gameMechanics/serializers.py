# serializers.py
from rest_framework import serializers
from .models import ReactionCard, ActionCard

class ReactionCardDataSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()

    class Meta:
        model = ReactionCard
        fields = ['id','name', 'description', 'values', 'playerType', 'price', 'type', 'image']

class ActionCardDataSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()

    class Meta:
        model = ActionCard
        fields = ['id','name', 'description', 'playerType', 'price', 'pressure', 'image']
