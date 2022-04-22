import os
from .game import WordleGameHandler
from discord.ext.commands import Bot, Cog
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option


class WordleCog(Cog):

    def __init__(self, bot: Bot):
        self.bot = bot
        self.game_handler = WordleGameHandler()

    guild_ids = []
    if ',' in os.getenv('GUILD_IDS'):
        guild_ids = [int(guild_id) for guild_id in os.getenv('GUILD_IDS').split(',')]
    else:
        guild_ids = [int(os.getenv('GUILD_IDS'))]

    @cog_ext.cog_slash(name="wordle",
                       description="Submit a guess for the current Wordle game.  If there is no active game, a new one will be started.",
                       guild_ids=guild_ids,
                       options=[
                           create_option(
                               name="guess",
                               description="Your 5-letter guess",
                               option_type=3,  # string
                               required=True
                           )
                       ])
    async def _guess(self, ctx: SlashContext, **kwargs):
        guess = kwargs.get('guess')
        await self.game_handler.process_guess(ctx, guess)

    @cog_ext.cog_slash(name="wordle_about",
                       description="Info about the wordle bot.",
                       guild_ids=guild_ids)
    async def _about(self, ctx: SlashContext):
        await ctx.send("https://github.com/scottserven/disgamebot")


def setup(bot: Bot):
    bot.add_cog(WordleCog(bot))
