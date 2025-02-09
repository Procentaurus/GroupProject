from random import randint
from django.db.models import Q
from channels.db import database_sync_to_async
from django.forms import ValidationError

from gameMechanics.queries import get_r_card_sync

from .game_user.game_user import GameUser
from .game.game import Game
from .owned_reaction_card.owned_reaction_card import OwnedReactionCard
from .game_authentication_token.game_authentication_token \
    import GameAuthenticationToken
from .reaction_card_in_shop.reaction_card_in_shop \
    import ReactionCardInShop



########### GameUser ###########

@database_sync_to_async
def get_game_user(game_user_id):
    try:
        return GameUser.objects.get(id=game_user_id)
    except GameUser.DoesNotExist:
        return None

@database_sync_to_async
def get_game_user_with_user(user_id):
    try:
        return GameUser.objects.get(user_id=user_id)
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
def create_game_user(user_id, conflict_side, channel_name):
    game_user = GameUser.objects.create(
        user_id=user_id,
        conflict_side=conflict_side,
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
    except (GameAuthenticationToken.DoesNotExist, ValueError, ValidationError):
        return None

@database_sync_to_async
def delete_game_token(game_user):
    if game_user is not None:
        try:
            t = GameAuthenticationToken.objects.get(user_id=game_user.user_id)
            t.delete()
        except GameAuthenticationToken.DoesNotExist:
            pass



########### Game ###########

@database_sync_to_async
def get_game(game_id):
    try:
        return Game.objects.get(id=game_id)
    except Game.DoesNotExist:
        return None
 
@database_sync_to_async
def get_game_with_game_user(game_user):
    return Game.objects.filter(
        Q(teacher_player=game_user) | Q(student_player=game_user)
    ).first()

@database_sync_to_async
def create_game(teacher_player, student_player):
    number = randint(0,1)
    next_move_player = "teacher" if number == 0 else "student"
    game = Game.objects.create(
        teacher_player=teacher_player,
        student_player=student_player,
        next_move_player=next_move_player
    )
    return game

@database_sync_to_async
def delete_game(game_id):
    try:
        game = Game.objects.get(id=game_id)
        game.delete()
        return True
    except Game.DoesNotExist:
        return False



### owned reaction card ###

@database_sync_to_async
def get_owned_reaction_cards(game_user):
    owned_cards = OwnedReactionCard.objects.filter(game_user=game_user)
    return [
        {"card": owned_card.reaction_card, "amount": owned_card.amount}
        for owned_card in owned_cards
    ]

@database_sync_to_async
def check_reaction_card_owned(game_user, r_card_id, amount):  
    owned_r_card = OwnedReactionCard.objects.filter(
        reaction_card__id=r_card_id, game_user=game_user).first()

    if owned_r_card is not None:
        return True if owned_r_card.amount >= amount else False
    else: return False

@database_sync_to_async
def add_reaction_card_to_owned(game_user, r_card_id, amount):
    r_card = get_r_card_sync(r_card_id)

    # Retrieve the OwnedReactionCard instance or create a new one
    # if it doesn't exist
    (owned_card, _) = OwnedReactionCard.objects.get_or_create(
        game_user=game_user,
        reaction_card=r_card,
    )
    increase_card_amount(owned_card, amount)

@database_sync_to_async
def remove_reaction_card(game_user, r_card_id, amount):
    owned_r_card = OwnedReactionCard.objects.filter(
        reaction_card__id=r_card_id, game_user=game_user).first()

    if owned_r_card is not None:
        decrease_card_amount(owned_r_card, amount)



### reaction card in shop ###

@database_sync_to_async
def get_reaction_cards_in_shop(game_user):
    cards_in_shop = ReactionCardInShop.objects.filter(game_user=game_user)
    return [
        {"card": card_in_shop.reaction_card, "amount": card_in_shop.amount}
        for card_in_shop in cards_in_shop
    ]

@database_sync_to_async
def check_reaction_card_in_shop(game_user, r_card_id, amount):
    r_card_in_shop = ReactionCardInShop.objects.filter(
        reaction_card__id=r_card_id, game_user=game_user).first()
    
    if r_card_in_shop is not None:
        return True if r_card_in_shop.amount >= amount else False
    else:
        return False

@database_sync_to_async
def add_reaction_card_to_shop(game_user, r_card_id, amount):  
    r_card = get_r_card_sync(r_card_id)
    
    # Retrieve the ReactionCardInShop instance or create a new one
    # if it doesn't exist
    card_in_shop, _ = ReactionCardInShop.objects.get_or_create(
        game_user=game_user,
        reaction_card=r_card
    )
    increase_card_amount(card_in_shop, amount)

@database_sync_to_async  
def remove_reaction_card_from_shop(game_user, r_card_id, amount):
    r_card_in_shop = ReactionCardInShop.objects.filter(
        reaction_card__id=r_card_id, game_user=game_user).first()

    if r_card_in_shop is not None:
        decrease_card_amount(r_card_in_shop, amount)

@database_sync_to_async
def remove_all_reaction_cards_from_shop(game_user):
    r_cards_in_shop = ReactionCardInShop.objects.filter(game_user=game_user)

    for r_card in r_cards_in_shop:
        r_card.delete()
   
def increase_card_amount(card, amount):
    card.amount += amount
    card.save()

def decrease_card_amount(card, amount):
    if card.amount > amount:
        card.amount -= amount
        card.save()
    elif card.amount == amount:
        card.delete()
