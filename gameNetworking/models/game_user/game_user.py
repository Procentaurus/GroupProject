from uuid import uuid4
from django.db import models
from channels.db import database_sync_to_async
from django.conf import settings

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
    reroll_price = models.PositiveSmallIntegerField(default=30)
    owned_action_cards = models.ManyToManyField(
        ActionCard, related_name="owned_action_cards")
    action_cards_in_shop = models.ManyToManyField(
        ActionCard, related_name="action_cards_in_shop")
    
    action_moves_left = models.PositiveSmallIntegerField(default=0)
    reaction_moves_left = models.PositiveSmallIntegerField(default=0)
    opp_played_action_card_id = models.UUIDField(null=True)

    class Meta:
        ordering = ["started_waiting"]

    @database_sync_to_async
    def get_user(self):
        return self.user

    @database_sync_to_async
    def set_morale(self, morale):
        self.morale = morale
        self.save()

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
        self.state = state
        self.save(force_update=True)

    def can_afford_reroll(self):
        return self.money >= self.reroll_price
    
    @database_sync_to_async
    def increase_reroll_price(self):
        self.reroll_price += settings.REROLL_PRICE_INCREASE_VALUE
        self.save()

    async def buy_reroll(self):
        await self.subtract_money(self.reroll_price)

    def is_in_hub(self):
        return self.state == PlayerState.IN_HUB
    
    def wait_for_clash_end(self):
        return self.state == PlayerState.AWAIT_CLASH_END
    
    def is_in_clash(self):
        return self.state == PlayerState.IN_CLASH
    
    def wait_for_clash_start(self):
        return self.state == PlayerState.AWAIT_CLASH_START
    
    def is_teacher(self):
        return self.conflict_side == "teacher"

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
        remove_action_card_impl(self, action_card_id)
    
    @database_sync_to_async
    def remove_action_card_from_shop(self, action_card_id):
        remove_action_card_from_shop_impl(self, action_card_id)
        
    @database_sync_to_async
    def add_action_card(self, action_card_id):
        add_action_card_impl(self, action_card_id)
    
    @database_sync_to_async
    def add_action_card_to_shop(self, action_card_id):
        add_action_card_to_shop_impl(self, action_card_id)

    @database_sync_to_async
    def remove_all_action_cards_from_shop(self):
        remove_all_action_cards_from_shop_impl(self)

    @database_sync_to_async
    def save(self):
        save_impl(self)
