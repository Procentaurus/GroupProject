async def send_message_to_group(consumer, data, event):
    await consumer.channel_layer.group_send(
        f"game_{consumer.get_game().id}",
        {
            'type': event,
            **data,
        }
    )

async def send_message_to_opponent(consumer, data, event):
    await consumer.channel_layer.send(
        consumer.get_opponent().channel_name,
        {
            'type': event,
            **data,
        }
    )
