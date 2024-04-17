from gameMechanics.queries import get_a_card_sync


def check_action_card_owned_impl(game_user, a_card_id):
    try:
        game_user.owned_action_cards.get(id=a_card_id)
        return True
    except Exception as e:
        return False
    
def add_action_card_impl(game_user, a_card_id):
    action_card = get_a_card_sync(a_card_id)
    game_user.owned_action_cards.add(action_card)
    game_user.save()

def remove_action_card_impl(game_user, a_card_id):
    action_card = game_user.owned_action_cards.get(id=a_card_id)
    game_user.owned_action_cards.remove(action_card)
    game_user.save()

def check_action_card_in_shop_impl(game_user, a_card_id):
    try:
        game_user.action_cards_in_shop.get(id=a_card_id)
        return True
    except Exception as e:
        return False

def remove_action_card_from_shop_impl(game_user, a_card_id):
    action_card = game_user.action_cards_in_shop.get(id=a_card_id)
    game_user.action_cards_in_shop.remove(action_card)
    game_user.save()

def add_action_card_to_shop_impl(game_user, a_card_id):
    action_card = get_a_card_sync(a_card_id)
    game_user.action_cards_in_shop.add(action_card)
    game_user.save()

def remove_all_action_cards_from_shop_impl(game_user):
    action_cards_in_shop = game_user.action_cards_in_shop.all()
    for action_card in action_cards_in_shop:
        game_user.action_cards_in_shop.remove(action_card)

    game_user.save()
