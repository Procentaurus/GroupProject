from gameNetworking.mechanics.queries import *
from gameNetworking.serializers import GameSerializer


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
    
    await consumer.accept()
    game_user = await create_game_user(access_token, conflict_side, consumer.channel_name)
    is_teacher = True if game_user.conflict_side == "teacher" else False
    consumer.set_game_user_id(game_user.id)
    # await delete_game_token(game_user)

    number_of_teachers_waiting = await get_number_of_waiting_game_users("teacher")
    number_of_students_waiting = await get_number_of_waiting_game_users("student")

    if number_of_teachers_waiting > 0 and number_of_students_waiting > 0: # initialization of the game if there are mininimum 2 players waiting
        await initialize_game(consumer, game_user, is_teacher)
        await manage_first_tasks(consumer, is_teacher)
    else:
        pass

async def initialize_game(consumer, game_user, is_teacher):

    # Initializing game
    player2 = await get_longest_waiting_game_user("student") if is_teacher else await get_longest_waiting_game_user("teacher")
    player1 = game_user

    player1.in_game = True
    player2.in_game = True

    # creating game object
    game = await create_game(player1, player2)
    consumer.set_game_id(game.id)
    consumer.logger.debug("The game has started")

    consumer.set_opponent_channel_name(player2.channel_name)
    consumer.logger.debug(consumer.get_opponent_channel_name())
    game_serialized = GameSerializer(game).data

    # adding both players' channels to one group
    game_id = consumer.get_game_id()
    await consumer.channel_layer.group_add(f"game_{game_id}", player2.channel_name) # group name is game_{UUID of game entity object}
    await consumer.channel_layer.group_add(f"game_{game_id}", player1.channel_name) # -||-

    # sending info about game to players and opponent's consumer
    await consumer.send_message_to_opponent({"game_id": str(game_id), "channel_name": consumer.channel_name}, "game_creation")
    await consumer.send_message_to_opponent(game_serialized, "game_start")
    game_serialized["type"] = "game_start"
    await consumer.send_json(game_serialized)

async def manage_first_tasks(consumer, is_teacher):

    # TODO get first task to each player
    initial_task_for_student = None
    initial_task_for_teacher = None
    opponent_task, my_task = None, None

    opponent_task = initial_task_for_student if is_teacher else initial_task_for_teacher
    my_task = initial_task_for_teacher if is_teacher else initial_task_for_student

    # sending initial tasks to players
    await consumer.send_json({"type": "collect_action", "task": my_task})
    await consumer.send_message_to_opponent({"task": opponent_task}, "collect_action")
