from gameNetworking.enums import GameStage
from gameNetworking.queries import get_game
from .hub_stage import hub_stage_impl
from .clash_stage import clash_stage_impl


# Main game loop function responsible for taking care of user requests to socket
async def main_game_loop_impl(consumer, data):
    game_id = consumer.get_game_id()

    # Enters when game object exists and the game has started
    if game_id is not None:

        message_type = data.get('type')
        game = await get_game(game_id)
        await consumer.refresh_game_user()

        if consumer.get_game_stage() == GameStage.HUB:
            await hub_stage_impl(
                consumer, game, message_type, data) 
        else:
            await clash_stage_impl(
                consumer, game, message_type, data)
    else:
        game_user = consumer.get_game_user()
        await consumer.error(
            f"{game_user.conflict_side} player made move before the game "
            +" has started")
