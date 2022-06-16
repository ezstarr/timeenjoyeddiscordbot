import io
import os
import json
import logging
import random
import discord
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from discord.ext.commands import Bot, Cog
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option
import storage.base_storage

logger = logging.getLogger(__name__)

# Game storage can support multiple games, so we want a const for this one game
DB_GAME_NAME = "wordle"

# Tile colors
GRAY = "#787c7e"
GREEN = "#6aaa64"
YELLOW = "#c9b458"
BLACK = "#000000"
RED = "#cc6666"
WHITE = "#ffffff"

# Declaring these globally in case we ever want a variation
NUMBER_OF_GUESSES = 6
NUMBER_OF_LETTERS = 5

# our data directory is under the source file path
source_path = Path(__file__).resolve()
source_dir = source_path.parent

tile_font = ImageFont.truetype(f"{source_dir}/fonts/Roboto-Regular.ttf", 40)
message_font = ImageFont.truetype(f"{source_dir}/fonts/Roboto-Regular.ttf", 35)

dictionary = []
with open(f"{source_dir}/data/dictionary.txt", "r") as dictionary_file:
    dictionary.extend(dictionary_file.read().splitlines())

words = []
with open(f"{source_dir}/data/words.txt", "r") as word_file:
    words.extend(word_file.read().splitlines())
    dictionary.extend(words)


class WordleTile:
    """
    Represents a single tile, with a color and a letter.
    """

    def __init__(self):
        self.color = "#333"  # default of a dark gray
        self.letter = ' '    # default to a space just so the rendering functions doesn't fail
        self.font_color = "#000000"

    def __str__(self):
        return f"{self.letter} {self.color}"

    def from_dict(self, tile):
        self.color = tile.get('color')
        self.letter = tile.get('letter')
        self.font_color = tile.get('font_color')


class WordleBoard:
    """
    Represents an entire board, made of a multidimensional array of WordleTile instances
    """

    def __init__(self):
        self.board = []
        self._init_board(NUMBER_OF_GUESSES, NUMBER_OF_LETTERS)

    def __str__(self):
        result = ""
        for row in self.board:
            for col in row:
                result = result + " " + str(col) + " "
            result += "\n"
        return result

    def _init_board(self, row_count, col_count):
        for y in range(0, row_count):
            self.board.append([])
            for x in range(0, col_count):
                self.board[y].append(WordleTile())

    def get_tile(self, row, col):
        return self.board[row][col]

    def set_tile(self, row, col, color, letter):
        self.board[row][col].color = color
        self.board[row][col].letter = letter

    def from_dict(self, board):
        for y in range(0, len(board)):
            for x in range(0, len(board[y])):
                self.board[y][x].from_dict(board[y][x])


class WordleGameState:
    """
    Maintain the attributes needed to represent the current state of the board, so that it may be persisted and
    restored as needed.
    """

    def __init__(self):
        self.game_board_message_id = None  # the Discord message the correlates to our game board
        self.guess_count = 0
        self.solution = None
        self.channel_id = None
        self.is_over = False
        self.board = WordleBoard()

    def __str__(self):
        return f"solution: {self.solution}\nboard:\n{self.board}"

    def from_dict(self, game_state):
        self.game_board_message_id = game_state.get('game_board_message_id')
        self.guess_count = game_state.get('guess_count')
        self.solution = game_state.get('solution')
        self.channel_id = game_state.get('channel_id')
        self.is_over = game_state.get('is_over')
        self.board.from_dict(game_state.get('board'))


class WordleJSONEncoder(json.JSONEncoder):
    """
    Serialize the WordleGameState and all contained instances, into JSON, so that the state may be persisted
    """

    def default(self, obj):
        if isinstance(obj, WordleGameState):
            return {"class": "WordleGameState",
                    "game_board_message_id": obj.game_board_message_id,
                    "guess_count": obj.guess_count,
                    "solution": obj.solution,
                    "is_over": obj.is_over,
                    "board": obj.board}
        elif isinstance(obj, WordleBoard):
            return obj.board
        elif isinstance(obj, WordleTile):
            return {"class": "WordleTile",
                    "color": obj.color,
                    "letter": obj.letter}
        else:
            return json.JSONEncoder.default(self, obj)


class WordleGame:

    def __init__(self):
        """
        Constructor for a single game instance
        """
        self.max_guesses = 6  # correlates to the number of rows that will be displayed
        self.col_count = 5
        self.pixel_width = 400  # no point in going too big since Discord will scale it down anyway
        self.pixel_height = 550
        self.submitter = None
        self.current_message = ""
        self.game_state = WordleGameState()
        self._pick_random_word()

    def _pick_random_word(self):
        """
        From the words list, pick a random value and return it
        :return: a string value of the chosen word
        """
        self.game_state.solution = words[random.randint(0, len(words))]

    def render(self):
        """
        Render an image file that represents the current state of the game board.
        :return: the Image instance
        """
        board_padding = 20
        cell_padding: int = 3
        block_size = int((self.pixel_width - (board_padding * 2)) / 5)

        image = Image.new("RGB", (self.pixel_width, self.pixel_height))
        draw = ImageDraw.Draw(image)

        # Draw all the individual tiles
        for row in range(0, self.max_guesses):
            for col in range(0, self.col_count):
                block = self.game_state.board.get_tile(row, col)
                x1 = board_padding + (col * block_size) + cell_padding
                y1 = board_padding + (row * block_size) + cell_padding
                x2 = x1 + block_size - cell_padding
                y2 = y1 + block_size - cell_padding
                draw.rounded_rectangle(xy=((x1, y1), (x2, y2)),
                                       radius=4,
                                       fill=block.color)
                text_size = draw.textsize(text=block.letter.upper(), font=tile_font)

                # center the letter in the tile
                draw.text(xy=(x1 + (block_size - text_size[0]) / 2 - (cell_padding / 2),
                              y1 + (block_size - text_size[1]) / 2 - cell_padding),
                          text=block.letter.upper(),
                          font=tile_font
                          )

        # Render an optional message at the bottom of the board.  This may be an error, or indicate the end of a game.
        if self.current_message:
            y1 = board_padding + (block_size * self.max_guesses) + (cell_padding * 4)
            # If there are multiple lines, render each line horizontally centered
            for message_line in self.current_message.splitlines():
                text_size = draw.textsize(text=message_line, font=message_font)
                x1 = (self.pixel_width - text_size[0]) / 2
                if x1 < board_padding:
                    x1 = board_padding
                draw.text(xy=(x1,
                              y1),
                          text=message_line,
                          font=message_font)
                y1 += text_size[1] + (cell_padding * 2)

        return image

    def _check_valid_word(self, guess):
        """
        Check if the word is both the right length, and in the dictionary.  Will set the self.current_message as needed
        if the result is false.
        :param guess: the string the user submitted
        :return: boolean - True if all conditions are met
        """
        row = self.game_state.guess_count
        if len(guess) > self.col_count:
            self.current_message = f"Word too long"
            return False

        if len(guess) < self.col_count:
            self.current_message = f"Word too short"
            return False

        if guess.lower() not in dictionary:
            self.current_message = "Not in word list\nTry again"
            for x in range(0, len(guess)):
                self.game_state.board.set_tile(row, x, RED, guess[x])
            return False
        else:
            return True

    def _match_letters(self, guess):
        """
        For the submitted word, fill in the tiles on the game board with the appropriate letters and colors
        :param guess: the string the user submitted
        :return: nothing
        """
        row = self.game_state.guess_count

        # We want character lists of both the solution and guess so that we can modify the lists to remove characters
        # that match while looping over them.
        solution = list(self.game_state.solution)
        guess = list(guess)  # shadow the passed param as a list so that we can modify it

        # Find exact match tiles first, those will be green regardless of order, to handle cases where the user
        # guesses multiples of the same letter, but only one matches, and it's not the first instance of that letter.
        for x in range(0, len(guess)):
            self.game_state.board.set_tile(row, x, GRAY, guess[x])  # default all tiles to gray
            if guess[x] == solution[x]:
                self.game_state.board.set_tile(row, x, GREEN, guess[x])  # exact match on letter and position
                # The letters in solution and guess were used now, so clear them so that they don't end up getting used
                # again in the partial match loop next.  Make them different so that the empty values can't match.
                solution[x] = None
                guess[x] = ' '

        # second pass marks any letters remaining in the guess that weren't exact matches, but are partial matches
        for x in range(0, len(guess)):
            if guess[x] in solution:
                self.game_state.board.set_tile(row, x, YELLOW, guess[x])  # letter matches, but not the position
                solution[solution.index(guess[x])] = None

    def _check_winner(self, guess):
        """
        Check to see if the submission is an exact match, and update the game state accordingly if True.
        :param guess: the string the user submitted
        :return: True if the submission matches the solution
        """
        if guess == self.game_state.solution:
            self.current_message = f"{self.submitter}\nWins in {self.game_state.guess_count}!"
            self.game_state.is_over = True
            return True
        else:
            return False

    def _check_max_guesses(self):
        """
        Check if the game has reached its maximum number of attempts, and adjust the game state accordingly if it has.
        :return:
        """
        if self.game_state.guess_count == self.max_guesses:
            self.current_message = "Better luck next time"
            self.game_state.is_over = True

    def submit_guess(self, guess, submitter):
        """
        Processes a word submission.  Resets some parts of the game state itself, and delegate to
        other methods to validate specific criteria and further update the game state as necessary.
        :param guess: the string the user submitted
        :param submitter: the Discord author object of the user that submitted the attempt
        :return: nothing
        """
        self.current_message = ""
        self.submitter = submitter
        if self._check_valid_word(guess):
            self._match_letters(guess)
            self.game_state.guess_count += 1
            if not self._check_winner(guess):
                self._check_max_guesses()


class WordleDiscordHandler(Cog):
    """
    The Cog registers the slash commands with Discord, and handles when a user triggers a command
    """

    def __init__(self, bot: Bot, game_storage):
        self.bot = bot
        self._game_storage: storage.base_storage.BaseStorage = game_storage
        self._active_games = {}  # map of channel id -> game instance, assumes one active game per channel
        self._load_active_games()

    def _load_active_games(self):
        """
        If there were any active games when the program last shutdown, reload those game states
        :return:
        """
        if self._game_storage:
            game_states = self._game_storage.get_all_game_states(DB_GAME_NAME)
            for game_state in game_states:
                game = WordleGame()
                game.game_state.from_dict(json.loads(game_state['json_game_state']))
                self._active_games[game_state['channel_id']] = game

    # For the slash commands to register and work properly, we need to bind to particular server (guild) IDs.  There
    # was mention in forums that command will work without explicit server ID binding, but that did not appear to be
    # working during testing.
    guild_ids = []
    if os.getenv(('GUILD_IDS')):
        if ',' in os.getenv('GUILD_IDS'):
            guild_ids = [int(guild_id) for guild_id in os.getenv('GUILD_IDS').split(',')]
        else:
            guild_ids = [int(os.getenv('GUILD_IDS'))]

    @cog_ext.cog_slash(name="wordle_about",
                       description="Info about the wordle bot.",
                       guild_ids=guild_ids)
    async def _about(self, ctx: SlashContext):
        await ctx.send("https://github.com/scottserven/disgamebot")

    @cog_ext.cog_slash(name="wordle",
                       description="Submit a guess for the current Wordle game.  If there is no active game, "
                                   "a new one will be started.",
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

        # if a game isn't active, just start a new one
        game = self._active_games.get(ctx.channel_id)
        if not game or game.game_state.is_over:
            game = WordleGame()
            self._active_games[ctx.channel_id] = game

        # Check the user's guess, update the board, and post it to discord
        game.submit_guess(guess, ctx.author.nick or ctx.author.name)
        prior_message_id = game.game_state.game_board_message_id
        await self._update_board(game, ctx)

        # If there was a prior board posted to Discord for this game, delete that image.  We don't want to keep prior
        # boards around for the current game, only the final image
        if prior_message_id:
            prior_message = await ctx.channel.fetch_message(prior_message_id)
            await prior_message.delete()

        if self._game_storage:
            self._game_storage.save_game_state(game_name=DB_GAME_NAME,
                                               channel_id=ctx.channel_id,
                                               game_state=json.dumps(game.game_state, cls=WordleJSONEncoder))

    # @cog_ext.cog_slash(name="wordle_stats",
    #                    description = "View how many guesses you won.",
    #                   guild_ids=guild_ids,)

    @staticmethod
    async def _update_board(game: WordleGame, ctx: SlashContext):
        """
        Uploads the latest game board image to Discord, and keeps track of the new post in case we need to remove
        it later.
        :param game: a valid WordleGame instance
        :param ctx: a SlashContext object
        :return: nothing
        """
        image = game.render()
        arr = io.BytesIO()
        image.save(arr, format="JPEG")
        arr.seek(0)
        f = discord.File(arr, filename='wordle_board.jpg')
        game_board_message = await ctx.send(file=f)
        game.game_state.game_board_message_id = game_board_message.id
