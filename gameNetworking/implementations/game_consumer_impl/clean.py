from gameNetworking.queries import *

async def disconnect_impl(consumer, winner):

    game_id = consumer.get_game_id()
    game = await get_game(game_id)
    if game is not None:

        if game is not None:
            flag = await delete_game(game_id)
            if not flag:
                consumer.logger.error(
                    "Couldnt couldnt clean up memory after the game.")
                
        if consumer.get_closure_from_user_side():
            await consumer.send_message_to_opponent(
                {"winner" : winner}, "game_end")
        else:
            await consumer.send_message_to_opponent(
                {"winner" : winner, "after_disconnect" : True},
                "game_end")
                
    await consumer.channel_layer.group_discard(
        f"game_{game_id}", consumer.channel_name)
