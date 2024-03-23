from rest_framework import serializers

from .models import Game, GameAuthenticationToken


class GameSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Game
        fields = ['next_move_player', 'start_datetime']


class GameAuthenticationTokenPublicSerializer(serializers.ModelSerializer):

    class Meta:
        model = GameAuthenticationToken
        fields = ['id',]


class GameAuthenticationTokenAdminSerializer(serializers.ModelSerializer):

    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = GameAuthenticationToken
        fields = ['id', "user", 'issued']