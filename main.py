import discord
from dotenv import load_dotenv
import logging
import os
import storage.postgres
from datetime import datetime
import json
# imports for twitch announcements:
import requests
from discord.ext import tasks, commands
from discord.utils import get


# Opens .env file
load_dotenv(".env")
logger = logging.getLogger(__name__)


# assigns secret tokens:
# discord_guild = os.environ['DISCORD_GUILD']
# channel_id = os.environ['CHANNEL_ID']


# twitch announcements:
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)


# Authentication with Twitch API.
client_id = os.environ['CLIENT_ID']
client_secret = os.environ['CLIENT_SECRET']
body = {
    'client_id': client_id,
    'client_secret': client_secret,
    "grant_type": 'client_credentials'
}
r = requests.post('https://id.twitch.tv/oauth2/token', body)
keys = r.json()
headers = {
    'Client-ID': client_id,
    'Authorization': 'Bearer ' + keys['access_token']
}


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


# returns true of streamer is streaming
# def checkuser(streamer_name):
#     try:
#         stream = requests.get('https://api.twitch.tv/helix/streams?user_login=' + streamer_name,
#                               headers=headers)
#         if streamer_name is not None and str(stream) == '<Response [200]>':
#             stream_data = stream.json()
#
#             if len(stream_data['data']) == 1:
#                 return True, stream_data
#             else:
#                 return False, stream_data
#         else:
#             stream_data = None
#             return False, stream_data
#     except Exception as e:
#         self.log_and_print_exception(e)
#         stream_data = None
#         return False, stream_data


# Executes when bot is started
# @bot.event
# async def on_ready():
#     # Defines a loop that will run every 10 seconds (checks for live users every 10 seconds).
#     @tasks.loop(seconds=1000)
#     async def live_notifs_loop():
#         # Opens and reads the json file
#         with open('streamers.json', 'r') as file:
#             streamers = json.loads(file.read())
#         # Makes sure the json isn't empty before continuing.
#         if streamers is not None:
#             # Gets the guild, 'twitch streams' channel, and streaming role.
#             global discord_guild
#             global channel_id
#             guild = bot.get_guild(int(discord_guild))
#             channel = bot.get_channel(int(channel_id))
#             # role = get(guild.roles, id=1234567890) <- include to connect to a discord role
#             # Loops through the json and gets the key,value which in this case is the user_id and twitch_name of
#             # every item in the json.
#             for user_id, twitch_name in streamers.items():
#                 # Takes the given twitch_name and checks it using the checkuser function to see if they're live.
#                 # Returns either true or false.
#                 status = checkuser(twitch_name)
#                 # Gets the user using the collected user_id in the json
#                 user = bot.get_user(int(user_id))
#                 # Makes sure they're live
#                 if status is True:
#                     # Checks to see if the live message has already been sent.
#                     async for message in channel.history(limit=200):
#                         # If it has, break the loop (do nothing).
#                         if str(user.mention) in message.content and "is now streaming" in message.content:
#                             break
#                         # If it hasn't, assign them the streaming role and send the message.
#                         else:
#                             break
#                             # Gets all the members in your guild.
#                             # async for member in guild.fetch_members(limit=None):
#                             #     # If one of the id's of the members in your guild matches the one from the json and
#                             #     # they're live, give them the streaming role.
#                             #     if member.id == int(user_id):
#                             #         await member.add_roles(role)
#                             # # Sends the live notification to the 'twitch streams' channel then breaks the loop.
#                             # await channel.send(
#                             #     f":red_circle: **LIVE**\n{user.mention} is now streaming on Twitch!"
#                             #     f"\nhttps://www.twitch.tv/{twitch_name}")
#                             # print(f"{user} started streaming. Sending a notification.")
#                             # break
#                 # If they aren't live do this:
#                 else:
#                     pass
#                     # Gets all the members in your guild.
#                     # async for member in guild.fetch_members(limit=None):
#                     #     # If one of the id's of the members in your guild matches the one from the json and they're not
#                     #     # live, remove the streaming role.
#                     #     if member.id == int(user_id):
#                     #         await member.remove_roles(role)
#                     # # Checks to see if the live notification was sent.
#                     # async for message in channel.history(limit=200):
#                     #     # If it was, delete it.
#                     #     if str(user.mention) in message.content and "is now streaming" in message.content:
#                     #         await message.delete()
#     # Start your loop.
#     live_notifs_loop.start()


# Command to add Twitch usernames to the json.
@bot.command(name='timeenjoyed', help='Adds your Twitch to the live notifs.', pass_context=True)
async def add_twitch(ctx, twitch_name):
    # Opens and reads the json file.
    with open('streamers.json', 'r') as file:
        streamers = json.loads(file.read())

    # Gets the users id that called the command.
    user_id = ctx.author.id
    # Assigns their given twitch_name to their discord id and adds it to the streamers.json.
    streamers[user_id] = twitch_name

    # Adds the changes we made to the json file.
    with open('streamers.json', 'w') as file:
        file.write(json.dumps(streamers))
    # Tells the user it worked.
    await ctx.send(f"Added {twitch_name} for {ctx.author} to the notifications list.")


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
