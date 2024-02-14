from gameMechanics.models import ActionCard, ReactionCard


async def purchase_action_card(consumer, game_user, action_card_id):

    action_card_price = ActionCard.objects.get(id=action_card_id).price

    if game_user.money >= action_card_price:
        await game_user.add_action_card(action_card_id)
        await game_user.subtract_money(action_card_price)
        return True
    else:
        await consumer.critical_error(
            f"Too expensive action card: {action_card_id} passed validation.")
        return False

async def purchase_reaction_card(consumer, game_user, reaction_card_id, amount):

    reaction_card_price = ReactionCard.objects.get(id=reaction_card_id).price

    if game_user.money >= reaction_card_price * amount:
        await game_user.add_reaction_card(reaction_card_id, amount)
        await game_user.subtract_money(reaction_card_price * amount)
        return True
    else:
        await consumer.critical_error(
            f"Too expensive action card: {reaction_card_id} passed validation.")
        return False
