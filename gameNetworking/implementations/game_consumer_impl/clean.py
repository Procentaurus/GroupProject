from gameNetworking.queries import *


async def cleanup_impl(consumer): # standard cleanup procedure that should be triggered after consumer.close()
    consumer.closure_from_user_side = False
    await consumer.perform_cleanup()

async def perform_cleanup_impl(consumer): # is called after game's end, when the end was triggered by the opponent or from standard cleanup procedure

    game_id = consumer.get_game_id()

    if game_id is None: # block used when opponents consumer already deleted game and game users' data
        flag = await delete_game_user(consumer.get_game_user_id())
        if not flag:
            consumer.logger.warning("Couldnt delete GameUser from db.")
    else: # block used when no cleaning was perfomed by opponent's consumer
        
        game = await get_game(game_id)
        if game is not None:

            teacher_player = await game.get_teacher_player()
            student_player = await game.get_student_player()
            flag1, flag2, flag3 = None, None, None

            if student_player is not None:
                flag1 = await delete_game_user(student_player.id)
            if teacher_player is not None:
                flag2 = await delete_game_user(teacher_player.id)
            flag3 = await delete_game(game_id)

            if not flag3:
                consumer.logger.debug("Couldnt delete Game from db.")
            if not flag1 or not flag2:
                consumer.logger.debug("Couldnt delete GameUser from db.")

async def disconnect_impl(consumer):

    game_id = consumer.get_game_id()

    if consumer.get_closure_from_user_side():  # disconnnect from user side
        if game_id is not None:
            await consumer.send_message_to_opponent(None, "game_end")
        await consumer.perform_cleanup()
    if game_id is not None:
        await consumer.channel_layer.group_discard(f"game_{game_id}", consumer.channel_name)