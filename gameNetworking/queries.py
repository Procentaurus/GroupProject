from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.db.models import Q
from random import randint

from .models import GameAuthenticationToken, GameUser, Game


@database_sync_to_async
def get_game_user(token_id):
    try:
        return GameAuthenticationToken.objects.get(id=token_id).user
    except GameAuthenticationToken.DoesNotExist:
        return AnonymousUser()
    
@database_sync_to_async
def get_token(token_id):
    try:
        return GameAuthenticationToken.objects.get(id=token_id)
    except GameAuthenticationToken.DoesNotExist:
        return None
    

@database_sync_to_async
def create_game_user(token, conflict_side, channel_name):
    try:
        user = token.user
        game_user = GameUser.objects.create(user=user, conflict_side=conflict_side, channel_name=channel_name)
        return game_user
    except GameAuthenticationToken.DoesNotExist:
        return None
    

@database_sync_to_async
def get_longest_waiting_player(conflict_side):
    try:
        return GameUser.objects.filter(conflict_side=conflict_side).first()
    except GameUser.DoesNotExist:
        return None


@database_sync_to_async
def get_number_of_waiting_players(conflict_side):
    return GameUser.objects.filter(Q(in_game=False) & Q(conflict_side=conflict_side)).count()


@database_sync_to_async
def create_game(teacher_player, student_player):
    try:
        number = randint(0,1)
        next_move = "teacher" if number == 0 else "student"
        game = Game.objects.create(teacher_player=teacher_player, student_player=student_player, next_move=next_move)
        return game
    except Game.DoesNotExist:
        return None
