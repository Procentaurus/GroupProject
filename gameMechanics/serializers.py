from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

from .models import ReactionCard, ActionCard

#
# Dto classes
#

class ReactionCardDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReactionCard
        fields = ['id','name', 'description', 'values', 'playerType', 'price','type']

class ActionCardDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = ActionCard
        fields = ['id','name', 'description', 'playerType', 'price', 'pressure']