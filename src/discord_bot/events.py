def setup_events(bot):

    async def discord_sender(channel, queue):
        while True:
            msg = await queue.get()
            await channel.send(msg)

    @bot.event
    async def on_ready():
        channel_normal = bot.get_channel(bot.normal_channel_id)
        channel_ping = bot.get_channel(bot.ping_channel_id)
        
        bot.loop.create_task(
            discord_sender(channel_normal, bot.messages_to_send)
        )
        bot.loop.create_task(
            discord_sender(channel_ping, bot.ping_queue)
        )