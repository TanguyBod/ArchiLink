def setup_events(bot):
    @bot.event
    async def on_ready():
        if not bot.world_manager.loaded:
            await bot.world_manager.load_worlds()
            bot.world_manager.loaded = True
            bot.custom_logger.info(f"{len(bot.world_manager.worlds)} worlds loaded, ready to accept commands.")
            
    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return  # Ignore messages from the bot itself

        if bot.user in message.mentions:
            bot.custom_logger.info(f"Bot mentioned in message from {message.author} trying to activate the tracker")
            command = bot.get_command("activate")
            ctx = await bot.get_context(message)
            await command.callback(ctx)
        
        await bot.process_commands(message)