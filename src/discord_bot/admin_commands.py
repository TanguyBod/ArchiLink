from archipelago.tracker_client import TrackerClient
import asyncio

async def is_admin(ctx, bot):
    if str(ctx.author.id) in bot.admins:
        return True
    else:
        return False

def setup_admin_commands(bot) :
    
    @bot.command(name='admin', help='Admin command')
    async def admin_command(ctx):
        if not await is_admin(ctx, bot):
            return
        await ctx.send('This is an admin command.')
    
    @bot.command(name='computeChecks')
    async def compute_checks(ctx):
        if not await is_admin(ctx, bot):
            return
        await ctx.send("Computing checks for all players. This may take a while...")
        try :
            for player in bot.bot_client.player_db.get_all_players():
                bot.logger.info(f"Computing checks for player {player.player_name}")
                tracker_client = TrackerClient(bot.config, bot.bot_client.logger, player.player_name)
                asyncio.create_task(tracker_client.run())
                await tracker_client.finished_event.wait()
                player.total_locations = tracker_client.total_locations
                player.checked_locations = tracker_client.checked_locations
            bot.logger.info("Checks computed for all players")
            await ctx.send("Checks computed for all players")
        except Exception as e:
            bot.logger.error(f"Error computing checks: {e}")
            await ctx.send(f"An error occurred while computing checks. Please try again later.")