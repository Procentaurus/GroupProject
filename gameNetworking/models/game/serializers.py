from rest_framework import serializers

from .game import Game


class GameReconnectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ['stage', 'moves_per_clash', 'turns_to_inc',
                  'next_move_player', 'next_move_type']
