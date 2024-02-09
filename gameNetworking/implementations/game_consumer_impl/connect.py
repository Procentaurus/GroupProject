from gameNetworking.queries import *


async def connect_impl(consumer): # main implementation function

    access_token = consumer.scope.get("token")
    conflict_side = consumer.scope["url_route"]["kwargs"]["conflict_side"]

    # check if user is using valid token
    if access_token is None:
        await consumer.close()
        return

    # check if user has chosen a playable conflict side
    if conflict_side != "teacher" and conflict_side != "student":
        await consumer.close()
        return
    
    game_user = await create_game_user(access_token, conflict_side, consumer.channel_name)
    is_teacher = True if game_user.conflict_side == "teacher" else False
    consumer.set_game_user_id(game_user.id)
    # await delete_game_token(game_user)

    number_of_teachers_waiting = await get_number_of_waiting_game_users("teacher")
    number_of_students_waiting = await get_number_of_waiting_game_users("student")

    await consumer.accept()

    # initialization of the game if there are mininimum 2 players waiting
    if number_of_teachers_waiting > 0 and number_of_students_waiting > 0:
        await initialize_game(consumer, game_user, is_teacher)
        # await initialize_game_archive()
        await manage_first_card_sets(consumer, is_teacher)

# Main initialization of the game game
async def initialize_game(consumer, game_user, is_teacher):
    
    player2 = await get_longest_waiting_game_user("student") if is_teacher else await get_longest_waiting_game_user("teacher")
    player1 = game_user

    player1.get_user().in_game = True
    player2.get_user().in_game = True

    # creating game object
    game = await create_game(player1, player2)
    consumer.set_game_id(game.id)
    consumer.logger.debug("The game has started.")

    # adding both players' channels to one group
    game_id = consumer.get_game_id()

    # group name is game_{UUID of game entity object}
    await consumer.channel_layer.group_add(f"game_{game_id}", player2.channel_name)
    await consumer.channel_layer.group_add(f"game_{game_id}", player1.channel_name)

    consumer.set_opponent_channel_name(player2.channel_name)

    # Triggering initialization on opponent site
    await consumer.send_message_to_opponent({"game_id": str(game_id), "channel_name": consumer.channel_name}, "game_creation")

    # Sending initial message about game start
    await consumer.send_message_to_opponent(None, "game_start")
    await consumer.send_json({'type': "game_start"})

async def manage_first_card_sets(consumer, is_teacher):

    # TODO get cards to send for both players
    initial_cards_for_teacher = None
    initial_cards_for_student = None

    opponent_cards = initial_cards_for_student if is_teacher else initial_cards_for_teacher
    my_cards = initial_cards_for_teacher if is_teacher else initial_cards_for_student

    # sending initial sets of cards to players
    await consumer.send_json({"type": "card_action", "cards": my_cards})
    await consumer.send_message_to_opponent({"cards": opponent_cards}, "card_action")
