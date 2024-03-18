from gameMechanics.models import ActionCard, ReactionCard


async def purchase_action_card(consumer, card_id):

    card_price = ActionCard.objects.get(id=card_id).price
    g_u = consumer.get_game_user()

    if g_u.money >= card_price:
        await g_u.add_action_card(card_id)
        await g_u.subtract_money(card_price)
    else:
        await consumer.critical_error(
            f"Too expensive action card: {card_id} passed validation.")

async def purchase_reaction_card(consumer, card_id, amount):

    card_price = ReactionCard.objects.get(id=card_id).price
    g_u = consumer.get_game_user()

    if g_u.money >= card_price * amount:
        await g_u.add_reaction_card(card_id, amount)
        await g_u.subtract_money(card_price * amount)
    else:
        await consumer.critical_error(
            f"Too expensive reaction card: {card_id} passed validation.")
