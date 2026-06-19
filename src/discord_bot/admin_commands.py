from archipelago.tracker_client import TrackerClient
from world.world_config import WorldConfigSelection
from utils.config import check_config
import discord
import asyncio
import os

async def is_admin(ctx, session):
    admin_ids = session.admin_ids
    if admin_ids == [] :
        return True # If no admin ids are specified, allow everyone to use admin commands
    return ctx.author.id in session.admin_ids

def setup_admin_commands(bot) :
    
    @bot.command(name='computeChecks')
    async def compute_checks(ctx):
        session = bot.world_manager.get_world_from_channel(ctx.channel.id)
        if session is None :
            bot.custom_logger.warning(f"Received message from channel {ctx.channel.id} but no world is associated to this channel.")
            await ctx.send("An error occurred while processing the command. Please try again later.")
            return
        if not await is_admin(ctx, session):
            await ctx.send("You don't have permission to use this command.")
            return
        await ctx.send("Computing checks for all players. This may take a while...")
        try :
            for player in session.bot_client.player_db.get_all_players():
                bot.custom_logger.info(f"Computing checks for player {player.player_name}")
                tracker_client = TrackerClient(session.bot_client.config, session.bot_client.logger, player.player_name)
                asyncio.create_task(tracker_client.run())
                await tracker_client.finished_event.wait()
                player.total_locations = tracker_client.total_locations
                player.checked_locations = tracker_client.checked_locations
            bot.custom_logger.info("Checks computed for all players")
            await ctx.send("Checks computed for all players")
        except Exception as e:
            bot.custom_logger.error(f"Error computing checks: {e}")
            await ctx.send(f"An error occurred while computing checks. Please try again later.")
            
    @bot.command(name="fastConfig", help="Quickly create a world with a default configuration. Usage: !fastConfig <ip_adress> <port> <password>")
    async def fast_config(ctx, ip_address, port, password=None):
        data = {
            "ArchipelagoConfig": {
                "client_url" : f"{ip_address}",
                "client_port" : f"{port}",
                "password" : password,
                "bot_slot" : "ArchiLink",
                "self_hosted" : "archipelago.gg" not in ip_address
            },
            "DiscordConfig": {
                "normal_channel_id" : f"{ctx.channel.id}",
                "ping_channel_id" : f"{ctx.channel.id}", 
                "admin_ids" : [ctx.author.id]
            },
            "AdvancedConfig": {
                "custom_deathlink_flavor" : False,
                "auto_ping_new_items" : True,
                "player_colors_limited" : False,
                "item_messages_in_thread" : False,
                "deathlink_messages_in_thread" : False
            }
        }
        datadir = os.getenv("DATA_DIRECTORY", "data")
        # Create a unique world ID 
        dt = discord.utils.utcnow()
        world_id = f"{ctx.author.id}_{int(discord.utils.time_snowflake(dt))}"
        world_data_dir = os.path.join(datadir, world_id)
        os.makedirs(world_data_dir, exist_ok=True)
        try:
            msg = await bot.world_manager.create_world(world_data_dir, data)
            if msg == "already_exists":
                await ctx.send("A world is already associated with this channel.\n\
Please delete the existing world before creating a new one or use a different normal channel in the configuration.")
                return
            await ctx.send(f"World created with fast configuration. You can now use the commands to interact with your world in {msg}.")
        except Exception as e:
            bot.custom_logger.error(f"Error creating world with fast configuration: {e}")
            await ctx.send(f"An error occurred while creating the world with fast configuration. Please try again later.")
            
    @bot.command(name="newWorld", help="Create a new world. Usage: !newWorld")
    async def new_world(ctx):
        data = {}
        view = WorldConfigSelection(author=ctx.author, data=data)
        await ctx.send(
            "Click to configure your world",
            view=view
        )
        await view.wait()
        data, valid = check_config(data)
        if not valid :
            await ctx.send("Invalid configuration, world creation cancelled. Please try again.")
            return
        
        datadir = os.getenv("DATA_DIRECTORY", "data")
        # Create a unique world ID 
        dt = discord.utils.utcnow()
        world_id = f"{ctx.author.id}_{int(discord.utils.time_snowflake(dt))}"
        world_data_dir = os.path.join(datadir, world_id)
        os.makedirs(world_data_dir, exist_ok=True)
        try:
            msg = await bot.world_manager.create_world(world_data_dir, data)
            if msg == "already_exists":
                await ctx.send("A world is already associated with the selected normal channel.\n\
Please delete the existing world before creating a new one or use a different normal channel in the configuration.")
                return
            await ctx.send(f"World created. You can now use the commands to interact with your world in {msg}.")
        except Exception as e:
            bot.custom_logger.error(f"Error creating world: {e}")
            await ctx.send(f"An error occurred while creating the world. Please try again later.")
            
    @bot.command(name="deleteWorld", help="Delete the world associated with the current channel. Usage: !deleteWorld")
    async def delete_world(ctx):
        session = bot.world_manager.get_world_from_channel(ctx.channel.id)
        if session is None :
            bot.custom_logger.warning(f"Received message from channel {ctx.channel.id} but no world is associated to this channel.")
            await ctx.send("No world is associated with this channel.")
            return
        if not await is_admin(ctx, session):
            await ctx.send("You don't have permission to use this command. Only the world admins can delete the world.")
            return
        try:
            await bot.world_manager.delete_world(session.world_id)
            await ctx.send("World deleted.")
        except Exception as e:
            bot.custom_logger.error(f"Error deleting world: {e}")
            await ctx.send(f"An error occurred while deleting the world. Please try again later.")
            
    @bot.command(name="listWorlds", help="List all worlds in the current discord server. Usage: !listWorlds")
    async def list_worlds(ctx):
        worlds = bot.world_manager.worlds
        if not worlds:
            await ctx.send("No worlds exist on this server.")
            return
        channel_link_list = []
        for session in worlds.values():
            normal_channel = bot.get_channel(session.normal_channel_id)
            if normal_channel and normal_channel.guild.id == ctx.guild.id:
                channel_link_list.append(f"https://discord.com/channels/{normal_channel.guild.id}/{normal_channel.id}")
        if not channel_link_list:
            await ctx.send("No worlds exist on this server.")
            return
        await ctx.send(f"There are {len(channel_link_list)} worlds on this server on the following channels:\n{chr(10).join(channel_link_list)}")

    @bot.command(name="isAdmin", help="Check if a user is an admin. Usage: !isAdmin")
    async def isadmin(ctx):
        session = bot.world_manager.get_world_from_channel(ctx.channel.id)
        if session is None:
            await ctx.send("No world is associated with this channel.")
            return False
        if ctx.author.id in session.admin_ids:
            await ctx.send("You are an admin.")
        else :
            await ctx.send("You are not an admin.")
            
    @bot.command(name="deactivate", help="Deactivate the bot and stop tracking this world. Usage: !deactivate")
    async def deactivate(ctx):
        session = bot.world_manager.get_world_from_channel(ctx.channel.id)
        bot.custom_logger.info(f"Received deactivate command from user {ctx.author.id} for world {session.world_id if session else 'unknown'}")
        if session is None:
            await ctx.send("No world is associated with this channel.")
            return
        if not await is_admin(ctx, session):
            await ctx.send("You don't have permission to use this command. Only the world admins can deactivate the bot.")
            return
        try:
            await session.bot_client.stop()
            await ctx.send("Bot deactivated. Tracking stopped for this world. To activate again, please use !activate.")
            bot.custom_logger.info(f"Bot deactivated for world {session.world_id} by user {ctx.author.id}")
        except Exception as e:
            bot.custom_logger.error(f"Error deactivating bot: {e}")
            await ctx.send(f"An error occurred while deactivating the bot. Please try again later.")
            
    @bot.command(name="activate", help="Activate the bot and start tracking this world. Usage: !activate")
    async def activate(ctx):
        session = bot.world_manager.get_world_from_channel(ctx.channel.id)
        bot.custom_logger.info(f"Received activate command from user {ctx.author.id} for world {session.world_id if session else 'unknown'}")
        if session is None:
            await ctx.send("No world is associated with this channel.")
            return
        if not await is_admin(ctx, session):
            await ctx.send("You don't have permission to use this command. Only the world admins can activate the bot.")
            return
        try:
            if session.bot_client.running:
                await ctx.send("Bot is already active and tracking this world.")
                return
            session.tasks.append(asyncio.create_task(session.bot_client.start()))
            # asyncio.create_task(session.bot_client.run())
            await ctx.send("Bot activated. Tracking started for this world.")
            bot.custom_logger.info(f"Bot activated for world {session.world_id} by user {ctx.author.id}")
        except Exception as e:
            bot.custom_logger.error(f"Error activating bot: {e}")
            await ctx.send(f"An error occurred while activating the bot. Please try again later.")
            
    @bot.command(name="config", help="Change the world configuration. Usage: !config <key> <new_value>")
    async def config_change(ctx, key_to_change, *, new_value) :
        """Change the world configuration. Usage: !config <key> <new_value>
        Fields that can be changed with this command are:
        - client_url
        - client_port
        - password
        - bot_slot
        - self_hosted
        - normal_channel_id
        - ping_channel_id
        - admin_ids (comma separated list of discord user ids)
        - custom_deathlink_flavor
        - auto_ping_new_items
        - player_colors_limited
        - item_messages_in_thread
        - deathlink_messages_in_thread  
        """
        session = bot.world_manager.get_world_from_channel(ctx.channel.id)
        if session is None:
            await ctx.send("No world is associated with this channel.")
            return
        if not await is_admin(ctx, session):
            await ctx.send("You don't have permission to use this command. Only the world admins can change the configuration.")
            return
        try:
            print(f"Attempting to change configuration key {key_to_change} to {new_value} for world {session.world_id}")
            allowed_keys = {}

            for section, values in session.bot_client.config.items():
                if isinstance(values, dict):
                    for key in values:
                        allowed_keys[key] = section
            if key_to_change not in allowed_keys:
                await ctx.send(
                    f"Invalid configuration key. Allowed keys are: {', '.join(allowed_keys.keys())}"
                )
                return
            section = allowed_keys[key_to_change]            
            current_value = session.bot_client.config[section][key_to_change]
            if isinstance(current_value, bool):
                new_value = new_value.lower() in ("true", "1", "yes")
            elif isinstance(current_value, int):
                new_value = int(new_value)
            elif isinstance(current_value, list):
                new_value = [int(x.strip()) for x in new_value.split(",")]
            elif current_value is None:
                if new_value.lower() == "null":
                    new_value = None
            session.bot_client.config[section][key_to_change] = new_value
            await ctx.send(f"Configuration updated: {key_to_change} is now set to {new_value}")
            # Recreate the bot client with the new configuration
            await ctx.send("Restarting the bot to apply the new configuration...")
            await bot.world_manager.restart_world(session.world_id)
            await ctx.send("Bot restarted with the new configuration.")
            
        except Exception as e:
            bot.custom_logger.error(f"Error changing configuration: {e}")
            await ctx.send(f"An error occurred while changing the configuration. Please make sure the new value is of the correct type and try again.")