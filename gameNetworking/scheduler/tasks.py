from channels.layers import get_channel_layer

from ..models.queries import get_game_user


async def limit_hub_time(user_id):
    user = await get_game_user(user_id)
    channel_layer = get_channel_layer()
    await channel_layer.send(
        user.channel_name,
        {'type': 'hub_stage_end'}
    )
