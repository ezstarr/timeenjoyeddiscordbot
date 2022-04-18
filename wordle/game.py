import io
import random
import discord
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path


"""
Global variables that we don't want to repeatedly instantiate
"""
GRAY = "#787c7e"
GREEN = "#6aaa64"
YELLOW = "#c9b458"
BLACK = "#000000"
RED = "#cc0000"

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


class WordleBoard:
    """
    Represents an entire board, made of a multidimensional array of WordleTile instances
    """

    def __init__(self, row_count, col_count):
        self.board = []
        self._init_board(row_count, col_count)

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


class WordleGameState:
    """
    Maintains several attributes which may change during the course of the game
    """

    def __init__(self):
        self.guess_count = 0
        self.is_over = False
        self.current_message = ""
        self.submission_author = None


class WordleGame:

    def __init__(self, game_author):
        """
        Constructor for a single game instance
        :param game_author: Discord account for the person that started the game
        """
        self.game_board_message = None  # the Discord message the correlates to our game board
        self.max_guesses = 6  # correlates to the number of rows that will be displayed
        self.col_count = 5
        self.pixel_width = 400  # no point in going too big since Discord will scale it down anyway
        self.pixel_height = 550
        self.board = WordleBoard(self.max_guesses, self.col_count)
        self.dictionary = []
        self.solution = self._pick_random_word()
        self.game_author = game_author
        self.game_state = WordleGameState()
        print(f"Solution: {self.solution}")

    def _pick_random_word(self):
        """
        From the words list, pick a random value and return it
        :return: a string value of the chosen word
        """
        return words[random.randint(0, len(words))]

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
                block = self.board.get_tile(row, col)
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
        if self.game_state.current_message:
            y1 = board_padding + (block_size * self.max_guesses) + (cell_padding * 4)
            # If there are multiple lines, render each line horizontally centered
            for message_line in self.game_state.current_message.splitlines():
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
        Check if the word is both the right length, and in the dictionary.  Will set the self.game_state.current_message as needed
        if the result is false.
        :param word: the string the user submitted
        :return: boolean - True if all conditions are met
        """
        row = self.game_state.guess_count
        if len(guess) > self.col_count:
            self.game_state.current_message = f"Word too long"
            return False

        if len(guess) < self.col_count:
            self.game_state.current_message = f"Word too short"
            return False

        if guess.lower() not in dictionary:
            self.game_state.current_message = "Not in word list"
            for x in range(0, len(guess)):
                self.board.set_tile(row, x, RED, guess[x])
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
        # We need a local copy of the solution because we're going to modify it as matches are found.  This is to
        # handle the case where a solution contains multiples of the same character, and we don't want to match on all
        # of them unless the user also has multiples of the same letter.
        solution = self.solution
        for x in range(0, len(guess)):
            if guess[x] in solution:
                if guess[x] == solution[x]:
                    self.board.set_tile(row, x, GREEN, guess[x])  # exact match on letter and position
                else:
                    self.board.set_tile(row, x, YELLOW, guess[x])  # letter matches, but not the position

                # Replace the matched letter in the solution, so we can't match on it again during this check.
                solution = solution.replace(guess[x], ' ', 1)
            else:
                self.board.set_tile(row, x, GRAY, guess[x])

    def _check_winner(self, guess):
        """
        Check to see if the submission is an exact match, and update the game state accordingly if True.
        :param guess: the string the user submitted
        :return: True if the submission matches the solution
        """
        if guess == self.solution:
            submitter = self.game_state.submission_author.nick or self.game_state.submission_author.name
            self.game_state.current_message = f"{submitter}\nWins in {self.game_state.guess_count}!"
            self.game_state.is_over = True

    def _check_max_guesses(self):
        """
        Check if the game has reached its maximum number of attempts, and adjust the game state accordingly if it has.
        :return:
        """
        if self.game_state.guess_count == self.max_guesses:
            self.game_state.current_message = "Better luck next time"
            self.game_state.is_over = True

    def submit_guess(self, guess, author):
        """
        Processes a word submission.  Resets some parts of the game state itself, and delegate to
        other methods to validate specific criteria and further update the game state as necessary.
        :param guess: the string the user submitted
        :param author: the Discord author object of the user that submitted the attempt
        :return: nothing
        """
        self.game_state.current_message = ""
        self.game_state.submission_author = author
        if self._check_valid_word(guess):
            self._match_letters(guess)
            self.game_state.guess_count += 1
            if not self._check_winner(guess):
                self._check_max_guesses()


class WordleGameHandler:
    """
    Manages the interaction between Discord commands and WordleGame instances
    """

    def __init__(self):
        # When the user types in a command that starts with this value, this handler will process the message
        self.command_prefix = "!wordle"

        # map of channel id -> game instance, assumes one active game per channel
        self.active_games = {}

    async def _update_board(self, game, message):
        """
        Uploads the latest game board image to Discord, and keeps track of the new post in case we need to remove
        it later.
        :param game: a valid WordleGame instance
        :param message: a Discord message object
        :return: nothing
        """
        image = game.render()
        arr = io.BytesIO()
        image.save(arr, format="JPEG")
        arr.seek(0)
        f = discord.File(arr, filename='wordle_board.jpg')
        game.game_board_message = await message.channel.send(file=f)

    async def process_message(self, message):
        """
        Process any messages from Discord that matched the self.command_prefix
        :param message: a Discord message object
        :return: nothing
        """
        # always delete the command message the user submitted, to keep the channel clean
        await message.channel.delete_messages([message])

        # display some help if they only enter !wordle
        if ' ' not in message.content:
            await message.channel.send('type !wordle followed by a 5 letter word to submit a guess.  A new game will automatically start if one is not already in-progress')
            return

        # if there was something after !wordle, that would be a word guess
        guess = message.content.split(' ')[1].lower()

        # if a game isn't active, just start a new one
        game = self.active_games.get(message.channel.id)
        if not game or game.game_state.is_over:
            print(message.channel.id)
            game = WordleGame(message.author)
            self.active_games[message.channel.id] = game

        # Check the users guess, update the board, and post it to discord
        game.submit_guess(guess, message.author)
        prior_message = game.game_board_message
        await self._update_board(game, message)

        # If there was a prior board displayed for this game, delete that image.  We don't want to keep prior boards
        # around for the current game, only the final one
        if prior_message:
            await message.channel.delete_messages([prior_message])


