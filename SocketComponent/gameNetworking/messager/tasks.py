from channels.layers import get_channel_layer

from ..models.queries import get_game_user, delete_game
from .scheduler import delete_player_states_queue, remove_game_state

async def limit_hub_time(opponent_id):
    opponent = await get_game_user(opponent_id)
    if opponent:
        channel_layer = get_channel_layer()
        await channel_layer.send(
            opponent.channel_name,
            {'type': 'hub_stage_timeout'}
        )

async def limit_action_time(opponent_id):
    opponent = await get_game_user(opponent_id)
    if opponent:
        channel_layer = get_channel_layer()
        await channel_layer.send(
            opponent.channel_name,
            {'type': 'action_move_timeout'}
        )

async def limit_reaction_time(opponent_id):
    opponent = await get_game_user(opponent_id)
    if opponent:
        channel_layer = get_channel_layer()
        await channel_layer.send(
            opponent.channel_name,
            {'type': 'reaction_move_timeout'}
        )

async def limit_game_data_lifetime(game_id):
    await delete_game(game_id)
    delete_player_states_queue(game_id)
    remove_game_state(game_id)

async def limit_game_state_lifetime(game_id):
    remove_game_state(game_id)

async def limit_opponent_rejoin_time(game_user_id):
    game_user = await get_game_user(game_user_id)
    if game_user:
        channel_layer = get_channel_layer()
        await channel_layer.send(
            game_user.channel_name,
            {
             'type': 'game_end',
             'winner': game_user.conflict_side,
             'after_surrender': True
            }
        )
