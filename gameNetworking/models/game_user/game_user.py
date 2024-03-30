from uuid import uuid4
from django.db import models
from channels.db import database_sync_to_async

from customUser.models import MyUser
from gameMechanics.models import ActionCard

from ...enums import PlayerState
from ..common import PLAYER_STATES, CONFLICT_SIDES
from .methods_impl import *
    

class GameUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE, null=False)

    started_waiting = models.DateTimeField(auto_now_add=True)
    channel_name = models.CharField(null=False, max_length=100)

    state = models.CharField(choices=PLAYER_STATES, default='in_hub',
        max_length=100, null=False, blank=False)
    morale = models.PositiveSmallIntegerField(
        default=100, null=False, blank=False)
    money = models.PositiveSmallIntegerField(
        default=500, null=False, blank=False)
    conflict_side = models.CharField(
        choices=CONFLICT_SIDES, null=False, max_length=15)

    owned_action_cards = models.ManyToManyField(
        ActionCard, related_name="owned_action_cards")
    action_cards_in_shop = models.ManyToManyField(
        ActionCard, related_name="action_cards_in_shop")

    class Meta:
        ordering = ["started_waiting"]

    @database_sync_to_async
    def get_user(self):
        return self.user

    @database_sync_to_async
    def set_morale(self, morale):
        self.morale = morale
        self.save()

    @database_sync_to_async
    def has_lost(self):
        return (self.morale <= 0)

    @database_sync_to_async
    def add_money(self, amount):
        self.money += amount
        self.save()

    @database_sync_to_async
    def subtract_money(self, amount):
        self.money -= amount
        self.save()

    @database_sync_to_async
    def set_state(self, state):
        self.state = state.value 
        self.save()

    @database_sync_to_async
    def is_in_hub(self):
        return self.state == PlayerState.IN_HUB
    
    @database_sync_to_async
    def wait_for_clash_end(self):
        return self.state == PlayerState.AWAIT_CLASH_END
    
    @database_sync_to_async
    def is_in_clash(self):
        return self.state == PlayerState.IN_CLASH
    
    @database_sync_to_async
    def wait_for_clash_start(self):
        return self.state == PlayerState.AWAIT_CLASH_START
    
    @database_sync_to_async
    def is_teacher(self):
        return self.conflict_side == "teacher"
    
    @database_sync_to_async
    def is_student(self):
        return self.conflict_side == "student"

    @database_sync_to_async
    def check_action_card_owned(self, action_card_id):
        result = check_action_card_owned_impl(self, action_card_id)
        return result
    
    @database_sync_to_async
    def check_action_card_in_shop(self, action_card_id):
        result = check_action_card_in_shop_impl(self, action_card_id)
        return result

    @database_sync_to_async
    def remove_action_card(self, action_card_id):
        result = remove_action_card_impl(self, action_card_id)
        return result
    
    @database_sync_to_async
    def remove_action_card_from_shop(self, action_card_id):
        result = remove_action_card_from_shop_impl(self, action_card_id)
        return result
        
    @database_sync_to_async
    def add_action_card(self, action_card_id):
        result = add_action_card_impl(self, action_card_id)
        return result
    
    @database_sync_to_async
    def add_action_card_to_shop(self, action_card_id):
        result = add_action_card_to_shop_impl(self, action_card_id)
        return result
