async def send_message_to_group_impl(consumer, data, event):
    await consumer.channel_layer.group_send(
        f"game_{consumer.get_game_id()}",
        {
            'type': event,
            **data,
        }
    )

async def send_message_to_opponent_impl(consumer, data, event):
    opponent_channel_name = consumer.get_opponent_channel_name()
    await consumer.channel_layer.send(
        opponent_channel_name,
        {
            'type': event,
            **data,
        }
    )
