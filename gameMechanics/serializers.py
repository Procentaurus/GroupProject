from rest_framework import serializers

from .models import ReactionCard, ActionCard

#
# Dto classes
#

class ReactionCardDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReactionCard
        fields = ['id','name', 'description', 'values', 'playerType', 'price', 'type']

class ActionCardDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = ActionCard
        fields = ['id','name', 'description', 'playerType', 'price', 'pressure']