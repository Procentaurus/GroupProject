from gameMechanics.models import ActionCard, ReactionCard
from gameMechanics.queries import *


async def check_all_cards_exist(consumer, action_cards_ids, reaction_cards_ids):
    not_existing_action_cards, not_existing_reaction_cards = [], []

    for action_card_id in action_cards_ids:
        action_card_exist = await check_action_card_exist(action_card_id)
        if not action_card_exist:
            not_existing_action_cards.append(action_card_id)

    for reaction_card_id in reaction_cards_ids:
        reaction_card_exist = await check_reaction_card_exist(reaction_card_id)
        if not reaction_card_exist:
            not_existing_reaction_cards.append(reaction_card_id)

    response_body = {}
    
    if(len(not_existing_action_cards) != 0):
        response_body["not_existing_action_cards"] = not_existing_action_cards

    if(len(not_existing_reaction_cards) != 0):
        response_body["not_existing_reaction_cards"] = not_existing_reaction_cards

    # if there is 1 or more not existing cards
    if response_body:
        await consumer.perform_complex_error_handling(
            f"Some action cards you have chosen do not exist.",
            f"Player chose not existing cards: {', '.join(not_existing_action_cards)}, \
            {', '.join(not_existing_reaction_cards)}",
            response_body)
        return False
    
    return True

async def check_all_cards_are_in_shop(consumer, game_user, action_cards_ids, reaction_cards_data):
    action_cards_not_in_shop, reaction_cards_not_in_shop = [], []

    for action_card_id in action_cards_ids:
        action_card_in_shop = await game_user.check_if_have_action_card_in_shop(action_card_id)
        if not action_card_in_shop:
            action_cards_not_in_shop.append(action_card_id)

    for reaction_card_data in reaction_cards_data:
        reaction_card_in_shop = await game_user.check_if_have_reaction_card_in_shop(
            reaction_card_data["reaction_card_id"], reaction_card_data["amount"])
        if not reaction_card_in_shop:
            reaction_cards_not_in_shop.append(reaction_card_data["reaction_card_id"])

    response_body = {}
    
    if(len(action_cards_not_in_shop) != 0):
        response_body["action_cards_not_in_shop"] = action_cards_not_in_shop

    if(len(reaction_cards_not_in_shop) != 0):
        response_body["reaction_cards_not_in_shop"] = reaction_cards_not_in_shop

    # when there is 1 or more cards that are no in the shop
    if response_body:
        await consumer.perform_complex_error_handling(
            f"Some action cards you have chosen are not in the shop.",
            f"Player chose cards outside his shop: {', '.join(action_cards_not_in_shop)}, \
            {', '.join(reaction_cards_not_in_shop)}",
            response_body)
        return False
    
    return True

async def check_game_user_can_afford_all_cards(consumer, game_user, action_cards_ids, reaction_cards_data):

    action_cards_total_price, action_cards_total_price = 0, 0

    for action_card_id in action_cards_ids:
        action_card = await get_action_card(action_card_id)
        if action_card is None:
            consumer.simple_error("Server error occured")
            consumer.logger.error(f"Not existing card passed validation: {action_card_id}")
        else:
            action_cards_total_price += action_card.price

    for reaction_card_data in reaction_cards_data:
        reaction_card = await get_reaction_card(reaction_card_data["reaction_card_id"])
        if reaction_card is None:
            consumer.simple_error("Server error occured")
            consumer.logger.error(f"Not existing card passed validation: {reaction_card_data['reaction_card_id']}")
        else:
            reaction_cards_total_price += reaction_card.price

    if game_user.money < action_cards_total_price + action_cards_total_price:
        await consumer.perform_error_handling(
            "You can not afford to buy all chosen cards.",
            "Player chose cards that he can not afford")
        return False
    
    return True

async def purchase_action_card(consumer, game_user, action_card_id):

    action_card_price = ActionCard.objects.get(id=action_card_id).price

    if game_user.money >= action_card_price:
        await game_user.add_action_card(action_card_id)
        await game_user.subtract_money(action_card_price)
        return True
    else:
        await consumer.perform_critical_error_handling(
            f"Too expensive action card: {action_card_id} passed validation.")
        return False

async def purchase_reaction_card(consumer, game_user, reaction_card_id, amount):

    reaction_card_price = ReactionCard.objects.get(id=reaction_card_id).price

    if game_user.money >= reaction_card_price * amount:
        await game_user.add_reaction_card(reaction_card_id, amount)
        await game_user.subtract_money(reaction_card_price * amount)
        return True
    else:
        await consumer.perform_critical_error_handling(
            f"Too expensive action card: {reaction_card_id} passed validation.")
        return False