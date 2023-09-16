import discord
import asyncio
from discord import app_commands
from discord.ext import commands
import dotenv
import logging
import os
# import storage.postgres
from datetime import datetime
import json


# Opens .env file
dotenv.load_dotenv(".env")
logger = logging.getLogger(__name__)


game_storage = None
storage_type = os.getenv("STORAGE_TYPE")
if storage_type:
    storage_type = storage_type.lower()
    if storage_type == 'postgres':
        game_storage = storage.postgres.PostgresStorage()


# Logs exception to .txt file.
def log_and_print_exception(e):
    logging_file = open("log.txt", "a")
    logging_file.write(f"{datetime.now()}\n{str(e)}\n\n")
    logging_file.close()
    print(f"Exception logged. Error:\n{e}")




def run_interaction_bot():
    # from discord.ext import commands
    bot = commands.Bot(command_prefix='', intents=discord.Intents.all())

    @bot.event
    async def on_ready():
        logger.info(f'{bot.user} has logged in.')
        await bot.tree.sync()
        print("Commands synced")

    import wordle
    asyncio.run(bot.add_cog(wordle.WordleDiscordHandler(bot, game_storage)))
    bot.run(os.getenv('BOT_TOKEN'))




run_interaction_bot()
