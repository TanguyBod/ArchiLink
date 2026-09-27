from world.world_manager import WorldManager
from discord_bot.bot import create_bot
from dotenv import load_dotenv
import asyncio
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
import os

# Create a logs directory at the same level as src if it doesn't exist
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)
log_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

logger = logging.getLogger("ArchiLink")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_format)

file_handler = TimedRotatingFileHandler(
    filename="logs/archilink.log",
    when="midnight",
    interval=1,
    backupCount=30,
    encoding="utf-8"
)

file_handler.suffix = "%Y-%m-%d"
file_handler.setFormatter(log_format)
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Put discord logger to warning to avoid cluttering the console with discord debug messages
logging.getLogger("discord").setLevel(logging.WARNING) 

async def main():
    # Load .env file
    if os.path.exists(".env"):
        load_dotenv()
    datadir = os.getenv("DATA_DIRECTORY", "data")
    os.makedirs(datadir, exist_ok=True)
    discord_bot = create_bot(logger)
    world_manager = WorldManager(discord_bot, logger, datadir)
    discord_bot.world_manager = world_manager # Give the bot a reference to the world manager so it can route messages to the correct world based on the channel they come from
    
    try :
        tasks = [
            asyncio.create_task(discord_bot.start(os.getenv("DISCORD_APP_TOKEN"))),
            asyncio.create_task(world_manager.autosave_all_worlds())
        ]
        await asyncio.gather(*tasks)
    
    except asyncio.CancelledError:
        logger.warning("Main task was cancelled.")
        raise

    except Exception as e:
        logger.exception("Fatal exception in main() : %s", e)
        for task in tasks:
            logger.error(
                "Task %s: done=%s cancelled=%s exception=%r",
                task.get_name(),
                task.done(),
                task.cancelled(),
                task.exception() if task.done() and not task.cancelled() else None
            )
        raise
    
    finally :
        logger.info("Shutting down, stopping all worlds...")
        # Close auto-save task
        if tasks[1] :
            tasks[1].cancel()
            try:
                await tasks[1]
            except asyncio.CancelledError:
                pass
        await world_manager.stop_all_worlds()
        await discord_bot.close()
        
    
if __name__ == "__main__":
    asyncio.run(main())