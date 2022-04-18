import dotenv
import discord
from wordle.game import WordleGameHandler

# List of registered game handlers, so this bot could handle more than one
game_handlers = [
    WordleGameHandler()
]

client = discord.Client()

@client.event
async def on_ready():
    pass


@client.event
async def on_message(message):
    # ignore messages from the bot itself
    if message.author == client.user:
        return

    for game_handler in game_handlers:
        if message.content.lower().startswith(game_handler.command_prefix.lower()):
            await game_handler.process_message(message)


config = dotenv.dotenv_values("env/.env")
client.run(config['BOT_TOKEN'])
