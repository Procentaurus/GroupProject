from gameNetworking.queries import *
from .main_game_loop.common import send_card_sets_to_shop


async def connect_impl(consumer): # main implementation function

    access_token = consumer.scope.get("token")
    conflict_side = consumer.scope["url_route"]["kwargs"]["conflict_side"]

    await consumer.accept()

    # check if user is using valid token
    if access_token is None:
        consumer.error("You have used invalid token",
            f"Invalid authentication token used by {conflict_side} player")
        await consumer.close()
        return

    # check if user has chosen a playable conflict side
    if conflict_side != "teacher" and conflict_side != "student":
        consumer.error("You have chosen invalid conflict side",
            f"Invalid conflict side chosen by {conflict_side} player")
        await consumer.close()
        return
    
    game_user = await create_game_user(
        access_token, conflict_side, consumer.channel_name)
    consumer.set_game_user(game_user)
    # await delete_game_token(game_user)

    number_of_teachers_waiting = await get_number_of_waiting_game_users("teacher")
    number_of_students_waiting = await get_number_of_waiting_game_users("student")

    # initialization of the game if there are mininimum 2 players waiting
    if number_of_teachers_waiting > 0 and number_of_students_waiting > 0:
        await initialize_game(consumer)
        # await initialize_game_archive()
        await send_card_sets_to_shop(consumer)

# Main initialization of the game
async def initialize_game(consumer):
    player_1 = consumer.get_game_user()
    player_2 = None
    if is_player_teacher(player_1):
        player_2 = await get_longest_waiting_game_user("student")
    else:
        player_2 = await get_longest_waiting_game_user("teacher")

    (await player_1.get_user()).in_game = True
    (await player_2.get_user()).in_game = True

    # Creating game object in DB
    game = await create_game(player_1, player_2)
    consumer.set_game_id(game.id)
    consumer.logger.info("The game has started.")

    # adding both players' channels to one group
    # group name is game_{UUID of game entity object}
    await consumer.channel_layer.group_add(f"game_{game.id}", player_2.channel_name)
    await consumer.channel_layer.group_add(f"game_{game.id}", player_1.channel_name)

    # Saves info about opponent's channels name
    consumer.set_opponent_channel_name(player_2.channel_name)

    # Triggering initialization on opponent site
    await consumer.send_message_to_opponent(
        {"game_id": str(game.id), "channel_name": consumer.channel_name},
        "game_creation")

    # Sending initial message about game start
    await consumer.send_message_to_opponent(
        {"initial_money_amount" : player_2.money,
        "initial_morale" : player_2.morale},
        "game_start")
    await consumer.game_start(
        {"initial_money_amount" : player_1.money,
        "initial_morale" : player_1.morale})

async def inform_about_improper_state_error(consumer, move_type):
    game_user = consumer.get_game_user()

    await consumer.critical_error(
        f"Improper state: {game_user.state} of {game_user.conflict_side}"
        + f" player in {move_type}.")

def is_player_teacher(player):
    return player.conflict_side == "teacher"
