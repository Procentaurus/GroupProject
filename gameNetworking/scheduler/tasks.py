from channels.layers import get_channel_layer

from ..models.queries import get_game_user, delete_game


async def limit_hub_time(user_id):
    user = await get_game_user(user_id)
    if user:
        channel_layer = get_channel_layer()
        await channel_layer.send(
            user.channel_name,
            {'type': 'hub_stage_timeout'}
        )

async def limit_action_time(user_id):
    user = await get_game_user(user_id)
    if user:
        channel_layer = get_channel_layer()
        await channel_layer.send(
            user.channel_name,
            {'type': 'action_move_timeout'}
        )

async def limit_reaction_time(user_id):
    user = await get_game_user(user_id)
    if user:
        channel_layer = get_channel_layer()
        await channel_layer.send(
            user.channel_name,
            {'type': 'reaction_move_timeout'}
        )

async def limit_game_data_lifetime(game_id):
    await delete_game(game_id)
