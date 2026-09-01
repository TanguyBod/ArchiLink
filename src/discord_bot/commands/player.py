from utils.commands import check_world_channel, get_current_player
from utils.name_finder import resolve_player_name
from models.discord_profil import DiscordProfile
from discord.ext import commands
from discord import app_commands
import discord

# ============================================================
# Utils for autocomplete
# ============================================================
    
async def autocomplete_player_name(interaction: discord.Interaction, current: str):
    session = await check_world_channel(interaction.client, interaction.channel.id)
    if session is None:
        return []
    player_names = session.bot_client.player_db.get_all_players_names()
    suggestions = [app_commands.Choice(name=player_name, value=player_name) for player_name in player_names if current.lower() in player_name.lower()]
    return suggestions[:25]

async def autocomplete_color(interaction: discord.Interaction, current: str):
    colors = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
    suggestions = [app_commands.Choice(name=color, value=color) for color in colors if current.lower() in color.lower()]
    return suggestions[:25]

class PlayerCog(commands.Cog):
    """Cog for player-related commands in the Discord bot."""

    def __init__(self, bot):
        self.bot = bot
        
    async def _players(self, channel_id) :
        session = await check_world_channel(self.bot, channel_id)
        if session is None :
            return "This channel is not associated to any world. Please use the commands in the correct channel or create a new world with !newWorld."
        players = session.bot_client.player_db.get_all_players_names()
        return f"Players in this multiworld are : {', '.join(players)}"
    
    async def _register(self, channel_id, author, player_name_asked) :
        session = await check_world_channel(self.bot, channel_id)
        if session is None :
            return "This channel is not associated to any world. Please use the commands in the correct channel or create a new world with !newWorld."
        # Check if player name is valid
        player_name = resolve_player_name(player_name_asked, session.bot_client.player_db.get_all_players_names())
        if player_name is None :
            return f"Player name {player_name_asked} not found. Please check the spelling and try again.\n\
Available player names are : {', '.join(session.bot_client.player_db.get_all_players_names())}"
        elif session.bot_client.player_db.get_player_by_name(player_name).discord_id is not None :
            player = session.bot_client.player_db.get_player_by_name(player_name)
            if player.discord_id == author.id :
                return f"You are already registered to player {player_name}."
            else :
                return f"Player {player_name} is already registered by {player.discord_id}.\nIf you think this is an error, please contact the administrator."
        else :
            discord_profil = session.bot_client.discord_db.get_discord_profile(author.id)
            if discord_profil is None :
                discord_profil = DiscordProfile(author.name, author.id)
            player = session.bot_client.player_db.get_player_by_name(player_name)
            # Link player and discord profile
            discord_profil.slots.append(player)
            discord_profil.current_slot = player
            session.bot_client.discord_db.add_discord_profile(discord_profil)
            session.bot_client.player_db.set_discord_id(player, discord_profil.id)
            return f"Player {player_name} successfully registered to discord user {author.name}#{author.discriminator}.\n\
You are currently registered to : {', '.join([p.player_name for p in discord_profil.slots])}"

    async def _unregister(self, channel_id, author, player_name: str = None) :
        session, discord_profil = await get_current_player(self.bot, channel_id, author)
        if session is None or discord_profil is None :
            return "No session or discord profile found. Please make sure you are in a valid game session and registered."
        registered_players = [p.player_name for p in discord_profil.slots] if discord_profil else []
        if registered_players == [] :
            return f"You are not registered to any player. Please register first using `!register <player_name>` command."
        player_name = resolve_player_name(player_name, registered_players) if player_name else None
        if player_name is not None and player_name not in registered_players :
            return f"You are not registered to player {player_name}. You are currently registered to : {', '.join(registered_players)}."
        elif player_name is not None and player_name in registered_players :
            player = session.bot_client.player_db.get_player_by_name(player_name)
            # Unlink player and discord profile
            discord_profil.slots.remove(player)
            session.bot_client.player_db.set_discord_id(player, None)
            return f"Player {player_name} successfully unregistered from discord user {author.name}#{author.discriminator}."
        else :
            # Unregister from all players
            for player in discord_profil.slots:
                session.bot_client.player_db.set_discord_id(player, None)
            discord_profil.slots.clear()
            return f"All players successfully unregistered from discord user {author.name}#{author.discriminator}."

    async def _current(self, channel_id, author) :
        session, discord_profil = await get_current_player(self.bot, channel_id, author)
        if session is None :
            return "This channel is not associated to any world. Please use the commands in the correct channel or create a new world with !newWorld."
        elif discord_profil is None :
            return "You are not registered to any player. Please register first using `!register <player_name>` command."
        else :
            current_player = discord_profil.current_slot
            return f"You are currently tracking {current_player.player_name}. Use `!switch` command to switch to another player if you are registered to multiple players."
    
    async def _switch(self, channel_id, author, player_name: str = None) :
        session, discord_profil = await get_current_player(self.bot, channel_id, author)
        if session is None or discord_profil is None :
            return "No session or discord profile found. Please make sure you are in a valid game session and registered."
        if player_name == None :
            # Switch to next slot in the list
            current_player = discord_profil.current_slot
            if current_player is None :
                discord_profil.current_slot = discord_profil.slots[0]
                return f"Successfully switched to player {discord_profil.slots[0].player_name}."
            else :
                current_index = discord_profil.slots.index(current_player)
                next_index = (current_index + 1) % len(discord_profil.slots)
                discord_profil.current_slot = discord_profil.slots[next_index]
                return f"Successfully switched to player {discord_profil.slots[next_index].player_name}."
        elif player_name not in [p.player_name for p in discord_profil.slots] :
            return f"You are not registered to player {player_name}. You are currently registered to : {', '.join([p.player_name for p in discord_profil.slots])}."
        else :
            player = session.bot_client.player_db.get_player_by_name(player_name)
            discord_profil.current_slot = player
            return f"Successfully switched to player {player_name}."
        
    async def _setcolor(self, channel_id, author, color: str, all: bool = False):
        session, discord_profil = await get_current_player(self.bot, channel_id, author)
        if session is None or discord_profil is None :
            return "No session or discord profile found. Please make sure you are in a valid game session and registered."
        player = discord_profil.current_slot
        colors = {
            "black": "\u001b[30m",
            "red": "\u001b[31m",
            "green": "\u001b[32m",
            "yellow": "\u001b[33m",
            "blue": "\u001b[34m",
            "magenta": "\u001b[35m",
            "cyan": "\u001b[36m",
            "white": "\u001b[37m",
        }
        if color.lower() not in colors:
            return f"Invalid color : {color}. Please choose from: black, red, green, yellow, blue, magenta, cyan, white."
        if all:
            for p in discord_profil.slots:
                p.color = colors[color.lower()]
                p.name_colored = f"{p.color}{p.player_name}\u001b[0m"
            return f"All your registered players' preferred color has been set to {color}."
        else :
            player.color = colors[color.lower()]
            player.name_colored = f"{player.color}{player.player_name}\u001b[0m"
            return f"Your preferred color has been set to {color}."
    
    # ============================================================
    # Prefix commands
    # ============================================================
    
    @commands.command(name='players')
    async def players(self, ctx):
        response = await self._players(ctx.channel.id)
        if response is not None:
            await ctx.send(response) 
            
    @commands.command(name='register')
    async def register(self, ctx, *, player_name: str) :
        response = await self._register(ctx.channel.id, ctx.author, player_name)
        if response is not None:
            await ctx.send(response)
            
    @commands.command(name='unregister')
    async def unregister(self, ctx, *, player_name: str = None) :
        response = await self._unregister(ctx.channel.id, ctx.author, player_name)
        if response is not None:
            await ctx.send(response)
            
    @commands.command(name='current')
    async def current(self, ctx) :
        response = await self._current(ctx.channel.id, ctx.author)
        if response is not None:
            await ctx.send(response)
            
    @commands.command(name='switch')
    async def switch(self, ctx, *, player_name: str = None) :
        response = await self._switch(ctx.channel.id, ctx.author, player_name)
        if response is not None:
            await ctx.send(response)
            
    @commands.command(name='setcolor', help='Set your preferred color.')
    async def setcolor(self, ctx, color: str, all: bool = False) :
        response = await self._setcolor(ctx.channel.id, ctx.author, color, all)
        if response is not None:
            await ctx.send(response)
    
    
    # ============================================================
    # Slash commands
    # ============================================================
    
    @app_commands.command(name='players', description='List all players in the current multiworld.')
    async def players_slash(self, interaction: discord.Interaction):
        await interaction.response.defer()
        response = await self._players(interaction.channel.id)
        if response is not None:
            await interaction.followup.send(response)
            
    @app_commands.command(name='register', description='Register yourself to a player.')
    @app_commands.describe(player_name='The name of the player you want to register to.')
    @app_commands.autocomplete(player_name=autocomplete_player_name)
    async def register_slash(self, interaction: discord.Interaction, player_name: str):
        await interaction.response.defer()
        response = await self._register(interaction.channel.id, interaction.user, player_name)
        if response is not None:
            await interaction.followup.send(response)
            
    @app_commands.command(name='unregister', description='Unregister yourself from a player.')
    @app_commands.describe(player_name='The name of the player you want to unregister from. If not provided, you will be unregistered from all registered players.')
    @app_commands.autocomplete(player_name=autocomplete_player_name)
    async def unregister_slash(self, interaction: discord.Interaction, player_name: str = None):
        await interaction.response.defer()
        response = await self._unregister(interaction.channel.id, interaction.user, player_name)
        if response is not None:
            await interaction.followup.send(response)
            
    @app_commands.command(name='current', description='Show the player you are currently tracking.')
    async def current_slash(self, interaction: discord.Interaction):
        await interaction.response.defer()
        response = await self._current(interaction.channel.id, interaction.user)
        if response is not None:
            await interaction.followup.send(response)

    @app_commands.command(name='switch', description='Switch to another player you are registered to.')
    @app_commands.describe(player_name='The name of the player you want to switch to. If not provided, you will switch to the next player in your registered list.')
    @app_commands.autocomplete(player_name=autocomplete_player_name)
    async def switch_slash(self, interaction: discord.Interaction, player_name: str = None):
        await interaction.response.defer()
        response = await self._switch(interaction.channel.id, interaction.user, player_name)
        if response is not None:
            await interaction.followup.send(response)

    @app_commands.command(name='setcolor', description='Set your preferred color.')
    @app_commands.describe(color='The color you want to set. Choose from: black, red, green, yellow, blue, magenta, cyan, white.', all='Set the color for all your registered players.')
    @app_commands.autocomplete(color=autocomplete_color)
    async def setcolor_slash(self, interaction: discord.Interaction, color: str, all: bool = False):
        await interaction.response.defer()
        response = await self._setcolor(interaction.channel.id, interaction.user, color, all)
        if response is not None:
            await interaction.followup.send(response)

async def setup(bot):
    await bot.add_cog(PlayerCog(bot))