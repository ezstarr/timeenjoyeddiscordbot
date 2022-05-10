import discord
import dotenv
import logging
import os
import storage.postgres

dotenv.load_dotenv(".env")
logger = logging.getLogger(__name__)

game_storage = None
storage_type = os.getenv("STORAGE_TYPE")
if storage_type:
    storage_type = storage_type.lower()
    if storage_type == 'postgres':
        game_storage = storage.postgres.PostgresStorage()


def run_interaction_bot():
    from discord_slash import SlashCommand
    from discord.ext import commands

    bot = commands.Bot(command_prefix='!', self_bot=True, intents=discord.Intents.all())
    SlashCommand(bot, sync_commands=True)

    @bot.event
    async def on_ready():
        logger.info(f'{bot.user} has logged in.')

    import wordle
    bot.add_cog(wordle.WordleDiscordHandler(bot, game_storage))
    bot.run(os.getenv('BOT_TOKEN'))


run_interaction_bot()
