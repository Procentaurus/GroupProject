from random import randint
from channels.db import database_sync_to_async
from django.db.models import Q

from .models import *


@database_sync_to_async
def get_action_cards(given_task, choice, number_of_cards_to_return):
    pass


@database_sync_to_async
def get_reaction_cards(given_task, choice, number_of_cards_to_return):
    pass


@database_sync_to_async
def calculate_change_in_morale(action_card, reaction_cards):
    pass