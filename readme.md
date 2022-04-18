# DisGameBot
### A Discord Game Bot

This was just a quick side project to have fun with.  

It only has a Wordle clone coded into it.  To play the game, type !wordle 
followed by a 5 letter word to submit a guess.  It will generate an image of 
the game board and upload that to Discord.  Keep using that command until you either
win or lose.

![Example Image](https://github.com/scottserven/disgamebot/blob/main/sample/sample.png)

It is structured so other games may be added to it at a later time.

## Try It Out
There is a test discord server running this bot if anybody wants to see it in action:

[DisGameBot's Test Server](https://discord.gg/42Cfxrw9)


## Getting Started

### Install Dependencies
```shell
pip install -r requirements.txt
```

### Create the .env File 
You will need to create an env/.env file.  A .env_sample is included, which you can copy, but you 
will need provide a Discord Bot Token that can be obtained from the Discord Developer Portal
at https://discord.com/developers/applications/

### Running the Bot
```shell
python main.py
```

