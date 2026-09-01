from utils.ansi import AnsiTable, AnsiText
from utils.commands import get_current_player
from discord.ext import commands
from discord import app_commands
import discord

async def send_new_items(bot, session, player) :
    user = await bot.fetch_user(player.discord_id)
    if user.dm_channel is None :
        await user.create_dm() 
    if player is None :
        session.bot_client.logger.error(f"Player with discord id {player.discord_id} not found.")
        return
    elif len(player.new_items) == 0 :
        session.bot_client.logger.info(f"Player found : {player.player_name} but no new items to send.")
        # DM player if no new items, to avoid spamming the channel
        await user.dm_channel.send("You have not received any new items since the last time you checked.")
    else :
        session.bot_client.logger.info(f"Player found : {player.player_name} with {len(player.new_items)} new items to send.")
        async with session.bot_client.lock:
            items = list(player.new_items)
            player.new_items.clear()
            
        table = AnsiTable(title="New Items Received", headers=["You", "Item", "Sender", "Location"])
        for item in items :
            table.add_row(
                AnsiText(player.player_name, color=player.color), 
                AnsiText(item.item_name),
                AnsiText(item.player_sending.player_name, color=item.player_sending.color),
                AnsiText(item.location_name)
            )
        await table.send(user.dm_channel)
        session.bot_client.logger.info(f"New items sent to {player.player_name} in DM.")
        
class NotificationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def _new(self, channel_id, author, all: str = None):
        session, discord_profil = await get_current_player(self.bot, channel_id, author)
        if session is None or discord_profil is None :
            return "No session or discord profile found. Please make sure you are in a valid game session and registered."
        if all == "all" :
            for player in discord_profil.slots :
                await send_new_items(self.bot, session, player)
            return "New items sent to your DM for all your registered players. Please check your messages."
        else :
            current_player = discord_profil.current_slot
            await send_new_items(self.bot, session, current_player)
            return "New items sent to your DM. Please check your messages."
            
    async def _enableping(self, channel_id, author):
        session, discord_profil = await get_current_player(self.bot, channel_id, author)
        if session is None or discord_profil is None :
            return "No session or discord profile found. Please make sure you are in a valid game session and registered."
        registered_players = [p.player_name for p in discord_profil.slots] if discord_profil else []
        if registered_players == [] :
            return "You are not registered to any player. Please register first using `!register <name>` command."
        else :
            for player in discord_profil.slots :
                player.allow_ping = True
            return "This discord bot will now ping you when another player finds an item relevant to your todo list."
            
    async def _disableping(self, channel_id, author):
        session, discord_profil = await get_current_player(self.bot, channel_id, author)
        if session is None or discord_profil is None :
            return "No session or discord profile found. Please make sure you are in a valid game session and registered."
        registered_players = [p.player_name for p in discord_profil.slots] if discord_profil else []
        if registered_players == [] :
            return "You are not registered to any player. Please register first using `!register <name>` command."
        else :
            for player in discord_profil.slots :
                player.allow_ping = False
            return "This discord bot won't bother you anymore with pings"
            
    async def _enablenewitems(self, channel_id, author):
        session, discord_profil = await get_current_player(self.bot, channel_id, author)
        if session is None or discord_profil is None :
            return "No session or discord profile found. Please make sure you are in a valid game session and registered."
        registered_players = [p.player_name for p in discord_profil.slots] if discord_profil else []
        if registered_players == [] :
            return "You are not registered to any player. Please register first using `!register <name>` command."
        else :
            for player in discord_profil.slots :
                player.get_new_items_auto = True
            return "You will now receive new items automatically in DM as soon as you start playing."
            
    async def _disablenewitems(self, channel_id, author):
        session, discord_profil = await get_current_player(self.bot, channel_id, author)
        if session is None or discord_profil is None :
            return "No session or discord profile found. Please make sure you are in a valid game session and registered."
        registered_players = [p.player_name for p in discord_profil.slots] if discord_profil else []
        if registered_players == [] :
            return "You are not registered to any player. Please register first using `!register <name>` command."
        else :
            for player in discord_profil.slots :
                player.get_new_items_auto = False
            return "You will now have to use `!new` command to check for new items received since the last time you checked."

    # ============================================================
    # Prefix commands
    # ============================================================
    
    @commands.command(name='new', description="Get new items received since the last time you checked.")
    async def new(self, ctx, all: str = None):
        response = await self._new(ctx.channel.id, ctx.author, all)
        await ctx.send(response)

    @commands.command(name='enableping', description="Enable ping when another player finds an item relevant to your todo list.")
    async def enableping(self, ctx):
        response = await self._enableping(ctx.channel.id, ctx.author)
        await ctx.send(response)

    @commands.command(name='disableping', description="Disable ping when another player finds an item relevant to your todo list.")
    async def disableping(self, ctx):
        response = await self._disableping(ctx.channel.id, ctx.author)
        await ctx.send(response)

    @commands.command(name='enablenewitems', description="Enable automatic sending of new items received in DM.")
    async def enablenewitems(self, ctx):
        response = await self._enablenewitems(ctx.channel.id, ctx.author)
        await ctx.send(response)

    @commands.command(name='disablenewitems', description="Disable automatic sending of new items received in DM.")
    async def disablenewitems(self, ctx):
        response = await self._disablenewitems(ctx.channel.id, ctx.author)
        await ctx.send(response)

    # ============================================================
    # Slash commands
    # ============================================================
    
    @app_commands.command(name='new', description="Get new items received since the last time you checked.")
    @app_commands.describe(all="If you want to get new items for all your registered players.")
    async def new_slash(self, interaction: discord.Interaction, all: str = None):
        await interaction.response.defer()
        response = await self._new(interaction.channel.id, interaction.user, all)
        await interaction.followup.send(response)

    @app_commands.command(name='enableping', description="Enable ping when another player finds an item relevant to your todo list.")
    async def enableping_slash(self, interaction: discord.Interaction):
        await interaction.response.defer()
        response = await self._enableping(interaction.channel.id, interaction.user)
        await interaction.followup.send(response)

    @app_commands.command(name='disableping', description="Disable ping when another player finds an item relevant to your todo list.")
    async def disableping_slash(self, interaction: discord.Interaction):
        await interaction.response.defer()
        response = await self._disableping(interaction.channel.id, interaction.user)
        await interaction.followup.send(response)

    @app_commands.command(name='enablenewitems', description="Enable automatic sending of new items received in DM.")
    async def enablenewitems_slash(self, interaction: discord.Interaction):
        await interaction.response.defer()
        response = await self._enablenewitems(interaction.channel.id, interaction.user)
        await interaction.followup.send(response)

    @app_commands.command(name='disablenewitems', description="Disable automatic sending of new items received in DM.")
    async def disablenewitems_slash(self, interaction: discord.Interaction):
        await interaction.response.defer()
        response = await self._disablenewitems(interaction.channel.id, interaction.user)
        await interaction.followup.send(response)

async def setup(bot):
    await bot.add_cog(NotificationCog(bot))