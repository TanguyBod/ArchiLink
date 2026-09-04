from archipelago.tracker_client import TrackerClient
from world.world_config import WorldConfigSelection
from utils.config import check_config
from discord.ext import commands
from discord import app_commands
import discord
import asyncio
import os

async def is_admin(author, session):
    admin_ids = session.admin_ids
    if admin_ids == [] :
        return True # If no admin ids are specified, allow everyone to use admin commands
    if author.id in admin_ids:
        return True
    roles = getattr(author, "roles", [])
    return any(role.id in admin_ids for role in roles)

class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    async def _computeChecks(self, channel_id) :
        session = self.bot.world_manager.get_world_from_channel(channel_id)
        if session is None :
            return "This channel is not associated to any world. Please use the commands in the correct channel or create a new world with !newWorld."
        await self.bot.get_channel(channel_id).send("Computing checks for all players. This may take a while...")
        try :
            for player in session.bot_client.player_db.get_all_players():
                self.bot.custom_logger.info(f"Computing checks for player {player.player_name}")
                tracker_client = TrackerClient(session.bot_client.config, session.bot_client.logger, player.player_name)
                asyncio.create_task(tracker_client.run())
                await tracker_client.finished_event.wait()
                player.total_locations = tracker_client.total_locations
                player.checked_locations = tracker_client.checked_locations
            self.bot.custom_logger.info("Checks computed for all players")
            return "Checks computed for all players"
        except Exception as e:
            self.bot.custom_logger.error(f"Error computing checks: {e}")
            return "An error occurred while computing checks. Please try again later."
            
    async def _fastConfig(self, channel_id, ip_address, port, author, password=None) :
        await self.bot.get_channel(channel_id).send("Creating world with fast configuration...")
        data = {
            "ArchipelagoConfig": {
                "client_url" : f"{ip_address}",
                "client_port" : f"{port}",
                "password" : password,
                "bot_slot" : "ArchiLink",
                "self_hosted" : "archipelago.gg" not in ip_address,
                "room_url" : ""
            },
            "DiscordConfig": {
                "normal_channel_id" : f"{channel_id}",
                "ping_channel_id" : f"{channel_id}", 
                "admin_ids" : [author.id]
            },
            "AdvancedConfig": {
                "custom_deathlink_flavor" : False,
                "new_items_on_join_game" : True,
                "player_colors_limited" : False,
                "item_messages_in_thread" : False,
                "deathlink_messages_in_thread" : False,
                "send_join_leave_messages" : True,
                "item_display_level" : 1,
                "display_traps" : True
            }
        }
        datadir = os.getenv("DATA_DIRECTORY", "data")
        # Create a unique world ID 
        dt = discord.utils.utcnow()
        world_id = f"{author.id}_{int(discord.utils.time_snowflake(dt))}"
        world_data_dir = os.path.join(datadir, world_id)
        os.makedirs(world_data_dir, exist_ok=True)
        try:
            msg = await self.bot.world_manager.create_world(world_data_dir, data)
            if msg == "already_exists":
                return "A world is already associated with this channel.\n\
Please delete the existing world before creating a new one or use a different normal channel in the configuration."
            elif msg == "bot_slot_missing":
                return "The bot slot 'ArchiLink' does not exist in the world. Please make sure the bot slot is created in the world before creating a new world with fast configuration.\nWorld creation cancelled."
            return f"World created with fast configuration. You can now use the commands to interact with your world in {msg}."
        except Exception as e:
            self.bot.custom_logger.error(f"Error creating world with fast configuration: {e}")
            return f"An error occurred while creating the world with fast configuration. Please try again later."
    
    async def _newWorld(self, channel_id, author) :
        data = {}
        view = WorldConfigSelection(author=author, data=data)
        await self.bot.get_channel(channel_id).send(
            "Click to configure your world",
            view=view
        )
        await view.wait()
        data, valid = check_config(data)
        if not valid :
            return "Invalid configuration, world creation cancelled. Please try again."
        
        datadir = os.getenv("DATA_DIRECTORY", "data")
        # Create a unique world ID 
        dt = discord.utils.utcnow()
        world_id = f"{author.id}_{int(discord.utils.time_snowflake(dt))}"
        world_data_dir = os.path.join(datadir, world_id)
        os.makedirs(world_data_dir, exist_ok=True)
        try:
            msg = await self.bot.world_manager.create_world(world_data_dir, data)
            if msg == "already_exists":
                return "A world is already associated with the selected normal channel.\n\
Please delete the existing world before creating a new one or use a different normal channel in the configuration."
            elif msg == "bot_slot_missing":
                return "The bot slot put in the config does not exist in the world. Please make sure the bot slot is created in the world before creating a new world.\nWorld creation cancelled."
            return f"World created. You can now use the commands to interact with your world in {msg}."
        except Exception as e:
            self.bot.custom_logger.error(f"Error creating world: {e}")
            return f"An error occurred while creating the world. Please try again later."
    
    async def _deleteWorld(self, channel_id, author) :
        session = self.bot.world_manager.get_world_from_channel(channel_id)
        if session is None :
            self.bot.custom_logger.warning(f"Received message from channel {channel_id} but no world is associated to this channel.")
            return "No world is associated with this channel."
        if not await is_admin(author, session):
            return "You don't have permission to use this command. Only the world admins can delete the world."
        
        try:
            await self.bot.world_manager.delete_world(session.world_id)
            return "World deleted."
        except Exception as e:
            self.bot.custom_logger.error(f"Error deleting world: {e}")
            return f"An error occurred while deleting the world. Please try again later."
            
    async def _listWorlds(self, channel_id) :
        worlds = self.bot.world_manager.worlds
        if not worlds:
            return "No worlds exist on this server."
        channel_link_list = []
        for session in worlds.values():
            normal_channel = self.bot.get_channel(session.normal_channel_id)
            if normal_channel and normal_channel.guild.id == self.bot.get_channel(channel_id).guild.id:
                channel_link_list.append(f"https://discord.com/channels/{normal_channel.guild.id}/{normal_channel.id}")
        if not channel_link_list:
            return "No worlds exist on this server."
        return f"There are {len(channel_link_list)} worlds on this server on the following channels:\n{chr(10).join(channel_link_list)}"

    async def _isAdmin(self, channel_id, author) :
        session = self.bot.world_manager.get_world_from_channel(channel_id)
        if session is None :
            return
        if await is_admin(author, session):
            return f"You are an admin for this world."
        else :
            return f"You are not an admin for this world."    
            
    async def _deactivate(self, channel_id) :
        session = self.bot.world_manager.get_world_from_channel(channel_id)
        if session is None :
            return "This channel is not associated to any world. Please use the commands in the correct channel or create a new world with !newWorld."
        try:
            await session.bot_client.stop()
            self.bot.custom_logger.info(f"Bot deactivated for world {session.world_id}")
            return "Bot deactivated."
        except Exception as e:
            self.bot.custom_logger.error(f"Error deactivating bot: {e}")
            return f"An error occurred while deactivating the bot. Please try again later."

    async def _activate(self, channel_id) :
        session = self.bot.world_manager.get_world_from_channel(channel_id)
        if session is None :
            return "This channel is not associated to any world. Please use the commands in the correct channel or create a new world with !newWorld."
        try:
            if session.bot_client.running:
                return "Bot is already active and tracking this world."
            session.tasks.append(asyncio.create_task(session.bot_client.start()))
            return "Bot activated. Tracking started for this world."
        except Exception as e:
            self.bot.custom_logger.error(f"Error activating bot: {e}")
            return f"An error occurred while activating the bot. Please try again later."
            
    async def _config(self, channel_id, key_to_change, new_value) :
        session = self.bot.world_manager.get_world_from_channel(channel_id)
        if session is None:
            return "This channel is not associated to any world. Please use the commands in the correct channel or create a new world with !newWorld."
        try:
            allowed_keys = {}
            for section, values in session.bot_client.config.items():
                if isinstance(values, dict):
                    for key in values:
                        allowed_keys[key] = section
            if key_to_change not in allowed_keys:
                return f"Invalid configuration key. Allowed keys are: {', '.join(allowed_keys.keys())}"
            section = allowed_keys[key_to_change]            
            current_value = session.bot_client.config[section][key_to_change]
            if isinstance(current_value, bool):
                new_value = new_value.lower() in ("true", "1", "yes")
            elif isinstance(current_value, int):
                new_value = int(new_value)
            elif isinstance(current_value, list):
                new_value = [int(x.strip()) for x in new_value.split(",")]
            elif isinstance(current_value, str):
                new_value = str(new_value)
            elif current_value is None:
                if new_value.lower() == "null":
                    new_value = None
            session.bot_client.config[section][key_to_change] = new_value
            # Restart the bot client to apply the new configuration
            self.bot.world_manager.restart_bot_client(session.world_id)
            return f"Configuration updated: {key_to_change} is now set to {new_value}"
        except Exception as e:
            self.bot.custom_logger.error(f"Error changing configuration: {e}")
            return f"An error occurred while changing the configuration. Please make sure the new value is of the correct type and try again."

    # ============================================================
    # Prefix commands
    # ============================================================
    
    @commands.command(name='computeChecks')
    async def compute_checks(self, ctx):
        response = await self._computeChecks(ctx.channel.id)
        await ctx.send(response)

    @commands.command(name="fastConfig", help="Quickly create a world with a default configuration. Usage: !fastConfig <ip_adress> <port> <optional_password>")
    async def fast_config(self, ctx, ip_address, port, password=None):
        response = await self._fastConfig(ctx.channel.id, ip_address, port, ctx.author, password)
        await ctx.send(response)

    @commands.command(name="newWorld", help="Create a new world. Usage: !newWorld")
    async def new_world(self, ctx):
        response = await self._newWorld(ctx.channel.id, ctx.author)
        await ctx.send(response)

    @commands.command(name="deleteWorld", help="Delete the world associated with the current channel. Usage: !deleteWorld")
    async def delete_world(self, ctx):
        response = await self._deleteWorld(ctx.channel.id, ctx.author)
        await ctx.send(response)

    @commands.command(name="listWorlds", help="List all worlds in the current discord server. Usage: !listWorlds")
    async def list_worlds(self, ctx):
        response = await self._listWorlds(ctx.channel.id)
        await ctx.send(response)

    @commands.command(name="isAdmin", help="Check if a user is an admin. Usage: !isAdmin")
    async def isadmin(self, ctx):
        response = await self._isAdmin(ctx.channel.id, ctx.author)
        await ctx.send(response)

    @commands.command(name="deactivate", help="Deactivate the bot and stop tracking this world. Usage: !deactivate")
    async def deactivate(self, ctx):
        response = await self._deactivate(ctx.channel.id)
        await ctx.send(response)

    @commands.command(name="activate", help="Activate the bot and start tracking this world. Usage: !activate")
    async def activate(self, ctx):
        response = await self._activate(ctx.channel.id)
        await ctx.send(response)

    @commands.command(name="config", help="Change the world configuration. Usage: !config <key> <new_value>")
    async def config_change(self, ctx, key_to_change, *, new_value) :
        response = await self._config(ctx.channel.id, key_to_change, new_value)
        await ctx.send(response)

    # ============================================================
    # Slash commands
    # ============================================================
    
    @app_commands.command(name='computechecks', description='Compute checks for all players in the world associated with this channel.')
    async def compute_checks_slash(self, interaction: discord.Interaction):
        await interaction.response.defer()
        response = await self._computeChecks(interaction.channel.id)
        await interaction.followup.send(response)

    @app_commands.command(name="fastconfig", description="Quickly create a world with a default configuration.")
    async def fast_config_slash(self, interaction: discord.Interaction, ip_address: str, port: str, password: str = None):
        await interaction.response.defer()
        response = await self._fastConfig(interaction.channel.id, ip_address, port, interaction.user, password)
        await interaction.followup.send(response)

    @app_commands.command(name="newworld", description="Create a new world. Usage: /newWorld")
    async def new_world_slash(self, interaction: discord.Interaction):
        await interaction.response.defer()
        response = await self._newWorld(interaction.channel.id, interaction.user)
        await interaction.followup.send(response)

    @app_commands.command(name="deleteworld", description="Delete the world associated with the current channel.")
    async def delete_world_slash(self, interaction: discord.Interaction):
        await interaction.response.defer()
        response = await self._deleteWorld(interaction.channel.id, interaction.user)
        await interaction.followup.send(response)

    @app_commands.command(name="listworlds", description="List all worlds in the current discord server.")
    async def list_worlds_slash(self, interaction: discord.Interaction):
        await interaction.response.defer()
        response = await self._listWorlds(interaction.channel.id)
        await interaction.followup.send(response)

    @app_commands.command(name="isadmin", description="Check if a user is an admin.")
    async def isadmin_slash(self, interaction: discord.Interaction):
        await interaction.response.defer()
        response = await self._isAdmin(interaction.channel.id, interaction.user)
        await interaction.followup.send(response)

    @app_commands.command(name="deactivate", description="Deactivate the bot and stop tracking this world.")
    async def deactivate_slash(self, interaction: discord.Interaction):
        await interaction.response.defer()
        response = await self._deactivate(interaction.channel.id)
        await interaction.followup.send(response)

    @app_commands.command(name="activate", description="Activate the bot and start tracking this world.")
    async def activate_slash(self, interaction: discord.Interaction):
        await interaction.response.defer()
        response = await self._activate(interaction.channel.id)
        await interaction.followup.send(response)
        
    @app_commands.command(name="config", description="Change the world configuration.")
    async def config_change_slash(self, interaction: discord.Interaction, key_to_change: str, new_value: str):
        await interaction.response.defer()
        response = await self._config(interaction.channel.id, key_to_change, new_value)
        await interaction.followup.send(response)

async def setup(bot):
    await bot.add_cog(AdminCog(bot))