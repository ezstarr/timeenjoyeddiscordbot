import logging
import dotenv
import discord
import os

logger = logging.getLogger(__name__)
dotenv.load_dotenv(".env")


def run_interaction_bot():
    from discord_slash import SlashCommand
    from discord.ext import commands

    bot = commands.Bot(command_prefix='!', self_bot=True, intents=discord.Intents.all())
    SlashCommand(bot, sync_commands=True)

    @bot.event
    async def on_ready():
        logger.info(f'{bot.user} has logged in.')

    bot.load_extension("wordle.cog")
    bot.run(os.getenv('BOT_TOKEN'))


try:
    run_interaction_bot()
except Exception as ex:
    logger.error(f"Exception occurred: {ex}")

