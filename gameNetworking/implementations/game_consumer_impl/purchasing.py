from gameMechanics.models import ActionCard, ReactionCard

from .messaging_decarators import *


async def purchase_action_card(consumer, game_user, action_card_id):
    flag_1 = await is_action_card_existing(consumer, action_card_id)
    flag_2 = await is_action_card_in_shop(consumer, game_user, action_card_id)

    if flag_1 and flag_2: # if both conditions are satisfied
        action_card_price = ActionCard.objects.get(id=action_card_id).price
        game_user_money = game_user.money

        if game_user_money >= action_card_price:
            await game_user.add_action_card(action_card_id)
            await game_user.subtract_money(action_card_price)
        else:
            consumer.error(f"You can not afford this action card: {action_card_id}")

async def purchase_reaction_card(consumer, game_user, reaction_card_id, amount):
    flag_1 = await is_reaction_card_existing(consumer, reaction_card_id)
    flag_2 = await is_reaction_card_in_shop(consumer, game_user, reaction_card_id)

    if flag_1 and flag_2: # if both conditions are satisfied
        reaction_card_price = ReactionCard.objects.get(id=reaction_card_id).price
        game_user_money = game_user.money

        if game_user_money >= reaction_card_price:
            await game_user.add_action_card(reaction_card_id)
            await game_user.subtract_money(reaction_card_price)
        else:
            consumer.error(f"You can not afford this reaction card: {reaction_card_id}")