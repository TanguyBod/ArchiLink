from utils.commands import get_current_player, check_world_channel
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm as cm
from io import BytesIO
from discord.ext import commands
from discord import app_commands
import discord
import time

class StatsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    async def _wastedOnArchipelago(self, channel_id, author) :
        session, discord_profil = await get_current_player(self.bot, channel_id, author)
        if session is None or discord_profil is None :
            return "No session or discord profile found. Please make sure you are in a valid game session and registered."
        player = discord_profil.current_slot
        if player.is_playing:
            player.time_played += time.time() - player.time_joined
            player.time_joined = time.time()
        time_played = player.time_played
        hours = int(time_played // 3600)
        minutes = int((time_played % 3600) // 60)
        seconds = int(time_played % 60)
        return f"You have wasted {hours} hours, {minutes} minutes and {seconds} seconds in this Archipelago Multiworld."

    async def _deaths(self, channel_id, author) :
        session, discord_profil = await get_current_player(self.bot, channel_id, author)
        if session is None or discord_profil is None :
            return "No session or discord profile found. Please make sure you are in a valid game session and registered."
        player = discord_profil.current_slot
        return f"You have died {len(player.deaths)} times."
        
    async def _deathgraph(self, channel_id, author) :
        session, discord_profil = await get_current_player(self.bot, channel_id, author)
        if session is None or discord_profil is None :
            return "No session or discord profile found. Please make sure you are in a valid game session and registered."
        player = discord_profil.current_slot
        if player.deaths == [] :
            return "You have not died yet. Congratulations !"
        else :
            deaths_minutes = [t / 60 for t in player.deaths]
            cumulative_deaths = list(range(1, len(deaths_minutes) + 1))
            deaths_minutes = [0] + deaths_minutes
            cumulative_deaths = [0] + cumulative_deaths
            plt.figure(figsize=(10,5))
            plt.step(deaths_minutes, cumulative_deaths, where='post')
            plt.scatter(deaths_minutes, cumulative_deaths)
            plt.title(f'{player.player_name} death graph')
            plt.xlabel('Time played (minutes)')
            plt.ylabel('Number of Deaths')
            buf = BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            file = discord.File(buf, filename='death_graph.png')
            # Close the plot to free memory
            plt.close()
            return file
            
    async def _globaldeaths(self, channel_id) :
        session = await check_world_channel(self.bot, channel_id)
        if session is None :
            return "No session or discord profile found. Please make sure you are in a valid game session and registered."
        deaths_dict = {}
        for player in session.bot_client.player_db.get_all_players() :
            deaths_dict[player.player_name] = len(player.deaths)
        plt.figure(figsize=(10,5))
        plt.bar(deaths_dict.keys(), deaths_dict.values())
        plt.title('Global Deaths')
        plt.xlabel('Player')
        plt.ylabel('Number of Deaths')
        plt.xticks(rotation=45)
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        file = discord.File(buf, filename='global_deaths.png')
        # Close the plot to free memory
        plt.close()
        return file
        
    async def _progress_graph(self, channel_id) :
        session = await check_world_channel(self.bot, channel_id)
        if session is None :
            return "No session or discord profile found. Please make sure you are in a valid game session and registered."
        percentage_dict = {}; checks_dict = {}
        for player in session.bot_client.player_db.get_all_players() :
            if player.total_locations <= 0 :
                return f"Error retrieving total locations for player {player.player_name}. Cannot compute progress graph.\n\
Ask an admin to run !computeChecks command first."
            percentage = (player.checked_locations / player.total_locations * 100) if player.total_locations > 0 else 0
            checks_dict[player.player_name] = player.checked_locations
            percentage_dict[player.player_name] = percentage
        num_players = len(percentage_dict)
        plt.figure(figsize=(max(10, num_players * 0.5), 8))
        values = list(percentage_dict.values())
        norm = mcolors.Normalize(vmin=0, vmax=100)
        cmap = cm.get_cmap('coolwarm')
        colors = [cmap(norm(v)) for v in values]
        bars = plt.bar(range(num_players), values, color=colors)
        for bar, player_name in zip(bars, percentage_dict.keys()):
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                height / 2,
                player_name,
                ha='center',
                va='center',
                rotation=90,
                fontsize=9,
                color='white',
                fontweight='bold'
            )
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                height + 1,
                str(checks_dict[player_name]),
                ha='center',
                va='bottom',
                fontsize=9
            )
        plt.title('Progress Graph', pad=25)
        plt.xlabel('Player')
        plt.ylabel('Percentage of checked locations')
        plt.xticks(range(num_players), [''] * num_players)
        plt.ylim(0, 100)
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        file = discord.File(buf, filename='progress_graph.png')
        plt.close()
        return file

    # ============================================================
    # Prefix commands
    # ============================================================
    
    @commands.command(name='wastedOnArchipelago')
    async def wastedOnArchipelago(self, ctx) :
        response = await self._wastedOnArchipelago(ctx.channel.id, ctx.author)
        await ctx.send(response)

    @commands.command(name='deaths')
    async def deaths(self, ctx) :
        response = await self._deaths(ctx.channel.id, ctx.author)
        await ctx.send(response)

    @commands.command(name='deathgraph')
    async def deathgraph(self, ctx) :
        response = await self._deathgraph(ctx.channel.id, ctx.author)
        if isinstance(response, str):  
            await ctx.send(response)
        else:   
            await ctx.send(file=response)
        
    @commands.command(name='globaldeaths')
    async def globaldeaths(self, ctx) :
        response = await self._globaldeaths(ctx.channel.id)
        if isinstance(response, str):
            await ctx.send(response)
        else:
            await ctx.send(file=response)
        
    @commands.command(name='progressGraph')
    async def progress_graph(self, ctx):
        response = await self._progress_graph(ctx.channel.id)
        if isinstance(response, str):
            await ctx.send(response)
        else:
            await ctx.send(file=response)

    # ============================================================
    # Slash commands
    # ============================================================
    
    @app_commands.command(name='wastedonarchipelago', description="Display the time you have played. The time is updated when you stop playing.")
    async def wastedOnArchipelago(self, interaction: discord.Interaction):
        await interaction.response.defer()
        response = await self._wastedOnArchipelago(interaction.channel.id, interaction.user)
        await interaction.followup.send(response)

    @app_commands.command(name='deaths', description="Display the number of deaths you have in this Archipelago Multiworld.")
    async def deaths(self, interaction: discord.Interaction):
        await interaction.response.defer()
        response = await self._deaths(interaction.channel.id, interaction.user)
        await interaction.followup.send(response)

    @app_commands.command(name='deathgraph', description="Display a graph of your deaths in this Archipelago Multiworld.")
    async def deathgraph(self, interaction: discord.Interaction):
        await interaction.response.defer()
        response = await self._deathgraph(interaction.channel.id, interaction.user)
        if isinstance(response, str):
            await interaction.followup.send(response)
        else:
            await interaction.followup.send(file=response)

    @app_commands.command(name='globaldeaths', description="Display a graph of the number of deaths of all players in this Archipelago Multiworld.")
    async def globaldeaths(self, interaction: discord.Interaction):
        await interaction.response.defer()
        response = await self._globaldeaths(interaction.channel.id)
        if isinstance(response, str):
            await interaction.followup.send(response)
        else:
            await interaction.followup.send(file=response)

    @app_commands.command(name='progressgraph', description="Display a graph of the progress of all players in this Archipelago Multiworld.")
    async def progress_graph(self, interaction: discord.Interaction):
        await interaction.response.defer()
        response = await self._progress_graph(interaction.channel.id)
        if isinstance(response, str):
            await interaction.followup.send(response)
        else:
            await interaction.followup.send(file=response)

async def setup(bot):
    await bot.add_cog(StatsCog(bot))