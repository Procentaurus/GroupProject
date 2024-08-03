from rest_framework import serializers

from .game_user import GameUser


class GameUserReconnectSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameUser
        fields = ['morale', 'money', 'reroll_price', 'action_moves_left',
                  'reaction_moves_left', 'conflict_side']
