# DisGameBot
### A Discord Game Bot

This was just a quick side project to have fun with.  

It only has a Wordle clone coded into it.  To play the game, type !wordle 
followed by a 5 letter word to submit a guess.  It will generate an image of 
the game board and upload that to Discord.  Keep using that command until you either
win or lose.

![Example Image](https://github.com/scottserven/disgamebot/blob/main/sample/sample.png)

It is structured so other games may be added to it at a later time.

# Try It Out
There is a public Discord server running this bot if you want to see it in action:

[DisGameBot's Test Server](https://discord.gg/42Cfxrw9)

# Running The Bot Yourself
Regardless of where you plan on hosting the app (on your own PC/server, or Heroku), the bot will 
need to be registered with Discord first.

## Discord Bot Registration

### Step 1 - Create Discord App
1) Go to https://discord.com/developers/applications and create a new Application.

* All **General Information** fields can be left as their default values.

### Step 2 - Bot Setup 
1) Go to the **Bot** menu and click **Add Bot**, and give it a name

2) Click **Reset Token**.  This will show your **Bot Token**.  Copy this somewhere, you will need it when running the bot.  If you lose it, you'll need to repeat this step and the ones after it again.

3) Under **Privileged Gateway Intents**, enable:
   * Presence Intent
   * Server Members Intent
   * Message Content Intent

### Step 3 - Grant Bot Permissions
1) Click the **OAuth2** menu at the left, then **URL Generator**.
2) Under **Scopes**, select
   * **bot** 
   * **applications.commands**

3) Under **Bot Permissions**, select 
   * **Send Messages**
   * **Manage Messages**
   
4) Copy the **Generated URL** at the bottom of the page, and paste that into your browser address bar.
5) Choose which Discord server you want to grant the bot those permissions on.


## Running on Heroku

You will need the following before running the commands below:
* A Heroku Account
* Your **Bot Token** from Discord (Step 2 above)
* Your Discord Server ID ([If you don't know how to get this](https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-))

To deploy to Heroku, clone this repo, and from within the repo folder:

```shell
heroku login
heroku create [some unique app name]
heroku config:set BOT_TOKEN=[your Discord Bot Token]
heroku config:set GUILD_IDS=[your Discord Server ID]
git push heroku main 
```


## Running Locally

You will need the following before running the commands below:
* Python 3.8.10 or higher 
* Your **Bot Token** from Discord (Step 2 above)
* Your Discord Server ID ([If you don't know how to get this](https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-))

### Setup the dotenv
You can either set environment variables, or put these variables in a env/.env file:
```shell
BOT_TOKEN=[your bot token]
GUILD_IDS[you server id]
```

### Run the Bot
```shell
python3 -m venv venv
. ./venv/bin/activate
pip install -r requirements.txt
python3 main.py
```


