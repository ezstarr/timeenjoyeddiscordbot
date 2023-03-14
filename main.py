import discord
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
    intents = discord.Intents.default()
    bot = commands.Bot(command_prefix='!', self_bot=True, intents=discord.Intents.all())
    tree = app_commands.CommandTree(bot)

    @bot.event
    async def on_ready():
        logger.info(f'{bot.user} has logged in.')


    @tree.command(name='sync', description='Owner only')
    async def sync(interaction: discord.Interaction, ctx):
        if interaction.user.id == os.getenv('BOT_ID'):
            await tree.sync()
            print('Command tree synced.')
        else:
            await ctx.send('You must be the owner to use this command!')


    import wordle
    bot.add_cog(wordle.WordleDiscordHandler(bot, game_storage))
    bot.run(os.getenv('BOT_TOKEN'))


run_interaction_bot()
