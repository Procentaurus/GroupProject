from gameMechanics.queries import *

from gameNetworking.enums import PlayerState


async def check_all_action_cards_exist(consumer, action_cards_ids):
    not_existing_action_cards = []

    for action_card_id in action_cards_ids:
        action_card_exist = await check_action_card_exist(action_card_id)
        if not action_card_exist:
            not_existing_action_cards.append(action_card_id)

    response_body = {}
    
    if(len(not_existing_action_cards) != 0):
        response_body["not_existing_action_cards"] = not_existing_action_cards

    # if there is 1 or more not existing cards
    if response_body:
        await consumer.complex_error(
            f"Some action cards you have chosen do not exist.",
            f"Player chose not existing cards: \
            {', '.join(not_existing_action_cards)}",
            response_body)
        return False
    return True

async def check_all_reaction_cards_exist(consumer, reaction_cards_ids):
    not_existing_reaction_cards = []

    for reaction_card_id in reaction_cards_ids:
        reaction_card_exist = await check_reaction_card_exist(reaction_card_id)
        if not reaction_card_exist:
            not_existing_reaction_cards.append(reaction_card_id)

    response_body = {}

    if(len(not_existing_reaction_cards) != 0):
        response_body["not_existing_reaction_cards"] = not_existing_reaction_cards

    # if there is 1 or more not existing cards
    if response_body:
        await consumer.complex_error(
            f"Some reaction cards you have chosen do not exist.",
            f"Player chose not existing cards: \
            {', '.join(not_existing_reaction_cards)}",
            response_body)
        return False
    return True

async def check_all_cards_are_in_shop(
        consumer, game_user, action_cards_ids, reaction_cards_data):
    
    action_cards_not_in_shop, reaction_cards_not_in_shop = [], []

    for action_card_id in action_cards_ids:
        action_card_in_shop = await game_user.check_if_have_action_card_in_shop(
            action_card_id)
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
        await consumer.complex_error(
            f"Some action cards you have chosen are not in the shop.",
            f"Player chose cards outside his shop: {', '.join(action_cards_not_in_shop)}, \
            {', '.join(reaction_cards_not_in_shop)}",
            response_body)
        return False
    return True

async def check_game_user_can_afford_all_cards(
        consumer, game_user, action_cards_ids, reaction_cards_data):

    action_cards_total_price, action_cards_total_price = 0, 0

    for action_card_id in action_cards_ids:
        action_card = await get_action_card(action_card_id)
        if action_card is None:
            await consumer.critical_error(
                f"Not existing card passed validation: {action_card_id}")
        else:
            action_cards_total_price += action_card.price

    for reaction_card_data in reaction_cards_data:
        reaction_card = await get_reaction_card(reaction_card_data["reaction_card_id"])
        if reaction_card is None:
            await consumer.critical_error(
                f"Not existing card passed validation: \
                {reaction_card_data['reaction_card_id']}")
        else:
            reaction_cards_total_price += reaction_card.price

    if game_user.money < action_cards_total_price + action_cards_total_price:
        await consumer.error(
            "You can not afford to buy all chosen cards.",
            "Player chose cards that he can not afford")
        return False
    return True

async def check_game_user_own_action_card(consumer, game_user, action_card_id):
    if not await game_user.check_if_own_action_card(action_card_id):
        await consumer.error_impl(
            "You don't own the used action card",
            f"The {game_user.conflict_side} player tried \
            to use {action_card_id} card that he does not posess.")
        return False
    return True

async def check_game_user_own_reaction_cards(consumer, game_user, reaction_cards_data):
    reaction_cards_not_owned = {}
    for reaction_card_data in reaction_cards_data:
        reaction_card_owned = await game_user.check_if_own_reaction_card(
            reaction_card_data["reaction_card_id"], reaction_card_data["amount"])
        if not reaction_card_owned:
            reaction_cards_not_owned.append(reaction_card_data["reaction_card_id"])

    response_body = {}

    if(len(reaction_cards_not_owned) != 0):
       response_body["reaction_cards_not_owned"] = reaction_cards_not_owned

    # when there is 1 or more cards that are no in the shop
    if response_body:
        await consumer.complex_error(
            "You don't own the used reaction card",
            f"Player chose cards outside his shop: {', '.join(reaction_cards_not_owned)}",
            response_body)
        return False
    return True

async def check_action_move_can_be_performed(consumer, game, game_user):
    
    is_player_turn = check_is_player_turn(consumer, game, game_user)
    if not is_player_turn: return False

    if game.next_move_type != "action":
        await consumer.error(
            "Wrong move. It is time for reaction.",
            f"{game_user.conflict_side} player performed move of wrong type.")
        return False
    
    # Check if player is in the clash stage, if not then flow error occured
    if game_user.state != PlayerState.IN_CLASH:
        await consumer.critical_error(
            f"Improper state {game_user.state} of {game_user.conflict_side} \
            player in clash action move.")
        return False
    
    return True

async def check_reaction_move_can_be_performed(
    consumer, game, game_user, reaction_cards_data):

    is_player_turn = check_is_player_turn(consumer, game, game_user)
    if not is_player_turn: return False

    if game.next_move_type != "action":
        await consumer.error(
            "Wrong move. It is time for action.",
            f"{game_user.conflict_side} player performed move of wrong type.")
        return False
    
    # Check if player is in the clash stage, if not then flow error occured
    if game_user.state != PlayerState.IN_CLASH \
        and game_user.state != PlayerState.AWAIT_CLASH_END:
        await consumer.critical_error(
            f"Improper state {game_user.state} of {game_user.conflict_side} \
            player in clash action move.")
        return False
    
    reaction_cards_ids = {x.get("reaction_card_id") for x in reaction_cards_data}
    reaction_card_exist = await check_all_reaction_cards_exist(
        consumer, reaction_cards_ids)
    if not reaction_card_exist: return False

    reaction_cards_are_owned = await check_game_user_own_reaction_cards(
        consumer, game_user, reaction_cards_data)
    if not reaction_cards_are_owned: return False

    return True

async def check_winner(
    consumer, game_user, opponent, new_player_morale, new_opponent_morale):
    
    if new_opponent_morale == 0:
        consumer.set_winner(game_user.get_conflict_side())
        await announce_winner(consumer, game_user)
        return True
    elif new_player_morale == 0:
        consumer.set_winner(opponent.get_conflict_side())
        await announce_winner(consumer, opponent)
        return True
    else: 
        return False
    
async def announce_winner(consumer):
    consumer.set_closure_from_user_side(False)
    await consumer.send_message_to_group(
        {"winner" : consumer.__winner},
        "game_end")
    
async def check_is_player_turn(consumer, game, game_user):
    if game.next_move_player != game_user.conflict_side:
        await consumer.error("Not your turn.",
            f"{game_user.conflict_side} player performed move \
            while it was not his turn.")
        return False
    return True
