from channels.layers import get_channel_layer

from ..models.queries import get_game_user, delete_game

async def limit_hub_time(opponent_id):
    opponent = await get_game_user(opponent_id)
    if opponent:
        print(f"limit_hub_time, opponent_state={opponent.state}, opponent_id={opponent_id}")
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
