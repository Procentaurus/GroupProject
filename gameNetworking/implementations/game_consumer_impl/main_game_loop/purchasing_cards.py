from gameMechanics.queries import get_action_card, get_reaction_card

from ....models.queries import add_reaction_card_to_owned

async def purchase_action_card(consumer, action_card_id):

    action_card_price = (await get_action_card(action_card_id)).price
    game_user = consumer.get_game_user()

    if game_user.money >= action_card_price:
        await game_user.add_action_card(action_card_id)
        await game_user.subtract_money(action_card_price)
    else:
        await consumer.critical_error(
            f"Too expensive action card: {action_card_id} passed validation.")

async def purchase_reaction_card(consumer, reaction_card_id, amount):

    reaction_card_price = (await get_reaction_card(reaction_card_id)).price
    game_user = consumer.get_game_user()

    if game_user.money >= reaction_card_price * amount:
        await add_reaction_card_to_owned(game_user, reaction_card_id, amount)
        await game_user.subtract_money(reaction_card_price * amount)
        return True
    else:
        await consumer.critical_error(
            f"Too expensive reaction card: {reaction_card_id} passed validation")
        return False
