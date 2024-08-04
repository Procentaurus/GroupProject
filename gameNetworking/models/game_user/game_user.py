from uuid import uuid4
from django.db import models
from channels.db import database_sync_to_async
from django.conf import settings

from customUser.models import MyUser
from gameMechanics.models import ActionCard

from ...scheduler.scheduler import check_game_user_state
from ...enums import PlayerState
from ..common import CONFLICT_SIDES
from .methods import *


class GameUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE, null=False)

    started_waiting = models.DateTimeField(auto_now_add=True)
    channel_name = models.CharField(null=False, max_length=100)

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
    opp_played_action_card_id = models.UUIDField(null=True, blank= True)

    class Meta:
        ordering = ["started_waiting"]

    #################################  Getters  ################################
    @database_sync_to_async
    def get_user(self):
        return self.user

    def has_lost(self):
        return (self.morale <= 0)
    
    def can_afford_reroll(self):
        return self.money >= self.reroll_price

    def is_in_hub(self, game_id):
        state = check_game_user_state(game_id, str(self.id))
        return state == PlayerState.IN_HUB

    def wait_for_clash_end(self, game_id):
        state = check_game_user_state(game_id, str(self.id))
        return state == PlayerState.AWAIT_CLASH_END

    def is_in_clash(self, game_id):
        state = check_game_user_state(game_id, str(self.id))
        return state == PlayerState.IN_CLASH

    def wait_for_clash_start(self, game_id):
        state = check_game_user_state(game_id, str(self.id))
        return state == PlayerState.AWAIT_CLASH_START

    def is_teacher(self):
        return self.conflict_side == "teacher"

    def is_student(self):
        return self.conflict_side == "student"

    @database_sync_to_async
    def get_owned_action_cards(self):
        return list(self.owned_action_cards.all())

    @database_sync_to_async
    def get_action_cards_in_shop(self):
        return list(self.action_cards_in_shop.all())

    @database_sync_to_async
    def check_action_card_owned(self, action_card_id):
        pass

    @database_sync_to_async
    def check_action_card_in_shop(self, action_card_id):
        pass

    #################################  Setters  ################################
    @database_sync_to_async
    def set_morale(self, morale):
        self.morale = morale
        self.save()

    @database_sync_to_async
    def add_money(self, amount):
        self.money += amount
        self.save()

    @database_sync_to_async
    def subtract_money(self, amount):
        self.money -= amount
        self.save()

    @database_sync_to_async
    def increase_reroll_price(self):
        self.reroll_price += settings.REROLL_PRICE_INCREASE_VALUE
        self.save()

    @database_sync_to_async
    def update_channel_name(self, channel_name):
        self.channel_name = channel_name
        self.save()

    #######################  State changing functions  #########################
    async def buy_reroll(self):
        pass

    @database_sync_to_async
    def remove_action_card(self, action_card_id):
        pass

    @database_sync_to_async
    def remove_action_card_from_shop(self, action_card_id):
        pass

    @database_sync_to_async
    def add_action_card(self, action_card_id):
        pass

    @database_sync_to_async
    def add_action_card_to_shop(self, action_card_id):
        pass

    @database_sync_to_async
    def remove_all_action_cards_from_shop(self):
        pass

    @database_sync_to_async
    def backup(self, consumer):
        pass

GameUser.backup = backup
GameUser.remove_all_action_cards_from_shop = remove_all_action_cards_from_shop
GameUser.add_action_card_to_shop = add_action_card_to_shop
GameUser.add_action_card = add_action_card
GameUser.remove_action_card_from_shop = remove_action_card_from_shop
GameUser.remove_action_card = remove_action_card
GameUser.check_action_card_in_shop = check_action_card_in_shop
GameUser.check_action_card_owned = check_action_card_owned
GameUser.buy_reroll = buy_reroll
