from gameMechanics.queries import check_action_card_exist, check_reaction_card_exist


async def is_action_card_owned(consumer, game_user, action_card_id):  
    action_card_owned = await game_user.check_if_own_action_card(action_card_id)
    if not action_card_owned:
        await consumer.error(f"You do not own this action card: {action_card_id}")
        return False
    return True

async def is_action_card_existing(consumer, action_card_id):  
    action_card_exist = await check_action_card_exist(action_card_id)
    if not action_card_exist:
        await consumer.error(f"Provided action card doesn't exist: {action_card_id}")
        return False
    return True
    
async def is_action_card_in_shop(consumer, game_user, action_card_id):  
    action_card_in_shop = await game_user.check_if_have_action_card_in_shop(action_card_id)
    if not action_card_in_shop:
        await consumer.error(f"You do not have this action card in shop: {action_card_id}")
        return False
    return True

async def is_reaction_card_owned(consumer, game_user, reaction_card_id, amount = 1):  
    reaction_card_owned = await game_user.check_if_own_reaction_card(reaction_card_id, amount)
    if not reaction_card_owned:
        await consumer.error(f"You do not own this reaction card: {reaction_card_id}")
        return False
    return True

async def is_reaction_card_existing(consumer, reaction_card_id):  
    reaction_card_exist = await check_reaction_card_exist(reaction_card_id)
    if not reaction_card_exist:
        await consumer.error(f"Provided reaction card doesn't exist: {reaction_card_id}")
        return False
    return True
    
async def is_reaction_card_in_shop(consumer, game_user, reaction_card_id, amount):
    reaction_card_in_shop = await game_user.check_if_have_reaction_card_in_shop(reaction_card_id, amount)
    if not reaction_card_in_shop:
        await consumer.error(f"You do not have this reaction card in shop: {reaction_card_id}")
        return False
    return True
