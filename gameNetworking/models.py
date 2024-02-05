from uuid import uuid4
from django.db import models
from channels.db import database_sync_to_async

from customUser.models import MyUser
from gameMechanics.models import *

from implementations.models_impl.game_user_impl import *
from implementations.models_impl.game_impl import *

#
# Implementation of all entity classes needed for the module
#

CONFLICT_SIDES = (
    ("teacher", "teacher"),
    ("student", "student"),
)

MOVE_TYPES = (
    ("action", "action"),
    ("reaction", "reaction")
)

PLAYER_STATES = (
    ('in_collecting', 'in_collecting'),
    ('await_clash_start', 'await_clash_start'),
    ('in_clash', 'in_clash'),
    ('await_clash_end', 'await_clash_end'),
)

class GameUser(models.Model): # user has new instance of GameUser created for every new game

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE, null=False)

    started_waiting = models.DateTimeField(auto_now_add=True)
    channel_name = models.CharField(null=False, max_length=100)
    in_game = models.BooleanField(default=False)

    current_state = models.CharField(choices=PLAYER_STATES, default='in_collecting', null=False, blank=False)
    morale = models.PositiveSmallIntegerField(default=100, null=False, blank=False)
    currency = models.PositiveSmallIntegerField(default=500, null=False, blank=False)
    conflict_side = models.CharField(choices=CONFLICT_SIDES, null=False, max_length=15)
    action_cards = models.ManyToManyField(ActionCard)
    reaction_cards = models.ManyToManyField(OwnedReactionCard, related_name='gameUser', blank=True)

    class Meta:
        ordering = ["started_waiting"]

    @database_sync_to_async
    def set_morale(self, morale):
        self.morale = morale
        self.save()

    @database_sync_to_async
    def set_current_state(self, state):
        self.current_state= state.value 
        self.save()

    @database_sync_to_async
    def check_if_own_action_card(self, action_card_id):
        result = check_if_own_action_card_impl(self, action_card_id)
        return result

    @database_sync_to_async
    def remove_action_card(self, action_card_id):
        result = remove_action_card_impl(self, action_card_id)
        return result
        
    @database_sync_to_async
    def add_action_card(self, action_card_id):
        result = add_action_card_impl(self, action_card_id)
        return result
        
    @database_sync_to_async
    def check_if_own_reaction_card(self, reaction_card_id, amount=1):
        result = check_if_own_reaction_card_impl(self, reaction_card_id, amount)
        return result

    @database_sync_to_async
    def remove_reaction_card(self, reaction_card_id, amount=1):
        result = remove_reaction_card_impl(self, reaction_card_id, amount)
        return result

    @database_sync_to_async
    def add_reaction_card(self, reaction_card_id, amount=1):
        result = add_reaction_card_impl(self, reaction_card_id, amount)
        return result
            

class Game(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    teacher_player = models.ForeignKey(GameUser, related_name="teacher_player", on_delete=models.SET_NULL, null=True)
    student_player = models.ForeignKey(GameUser, related_name="student_player", on_delete=models.SET_NULL, null=True)

    start_datetime = models.DateTimeField(auto_now_add=True)
    end_datetime = models.DateTimeField(null=True, blank=True)

    next_move_player = models.CharField(choices=CONFLICT_SIDES, max_length=15, null=False)
    next_move_type = models.CharField(choices=MOVE_TYPES, max_length=15, null=False, default="action")

    @database_sync_to_async
    def get_teacher_player(self):
        return self.teacher_player
        
    @database_sync_to_async
    def get_student_player(self):
        return self.student_player
    
    @database_sync_to_async
    def get_opponent_player(self, game_user_id):
        result = get_opponent_player_impl(self, game_user_id)
        return result
    

class GameAuthenticationToken(models.Model):  # entity class of single-use tokens needed to authenticate to websocket
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=False)
    issued = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-issued"]
        
    @database_sync_to_async
    def get_game_user(self):
        return self.user