from gameNetworking.queries import *

async def disconnect_impl(consumer):

    game_id = consumer.get_game_id()
    game = await get_game(game_id)
    if game is not None:

        if game is not None:
            flag = await delete_game(game_id)
            if not flag:
                consumer.logger.error(
                    "Couldnt couldnt clean up memory after the game.")
                
        if not consumer.get_closure_from_user_side():
            await consumer.send_message_to_opponent(
                {"winner" : consumer.get_winner()}, "game_end")
        else:
            await consumer.send_message_to_opponent(
                {"winner" : consumer.get_winner(), "after_disconnect" : True},
                "game_end")
                
    await consumer.channel_layer.group_discard(
        f"game_{game_id}", consumer.channel_name)
