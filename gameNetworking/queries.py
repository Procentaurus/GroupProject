from random import randint
from channels.db import database_sync_to_async

from .models import GameAuthenticationToken, GameUser, Game


########### GameUser ###########

@database_sync_to_async
def get_game_user(game_user_id):
    try:
        return GameUser.objects.get(id=game_user_id)
    except GameUser.DoesNotExist:
        return None
    
@database_sync_to_async
def get_longest_waiting_player(conflict_side):
    try:
        return GameUser.objects.filter(conflict_side=conflict_side).first()
    except GameUser.DoesNotExist:
        return None

@database_sync_to_async
def get_number_of_waiting_players(conflict_side):
    return GameUser.objects.filter(conflict_side=conflict_side).count()

@database_sync_to_async
def create_game_user(token, conflict_side, channel_name):
    user = token.user
    game_user = GameUser.objects.create(user=user, conflict_side=conflict_side,
        channel_name=channel_name)
    return game_user

@database_sync_to_async
def delete_game_user(game_user_id):
    try:
        game_user = GameUser.objects.get(id=game_user_id)
        game_user.delete()
        return True
    except GameUser.DoesNotExist:
        return False



########### GameAuthenticationToken ###########

@database_sync_to_async
def get_game_token(token_id):
    try:
        return GameAuthenticationToken.objects.get(id=token_id)
    except GameAuthenticationToken.DoesNotExist:
        return None    

@database_sync_to_async
def delete_game_token(game_user):

    if game_user is not None:
        my_user = game_user.user
        try:
            token = GameAuthenticationToken.objects.get(user=my_user)
            token.delete()
            return True
        except GameAuthenticationToken.DoesNotExist:
            return False
    else:
        return False



########### Game ###########

@database_sync_to_async
def get_game(game_id):
    try:
        return Game.objects.get(id=game_id)
    except Game.DoesNotExist:
        return None
    
@database_sync_to_async
def create_game(teacher_player, student_player):
    number = randint(0,1)
    next_move_player = "teacher" if number == 0 else "student"
    game = Game.objects.create(teacher_player=teacher_player,
        student_player=student_player, next_move_player=next_move_player)
    return game
    
@database_sync_to_async
def delete_game(game_id):
    try:
        game = Game.objects.get(id=game_id)
        game.delete()
        return True
    except Game.DoesNotExist:
        return False
