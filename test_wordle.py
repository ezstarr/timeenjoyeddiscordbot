import wordle
from wordle import WordleGame
import unittest


class TestWordle(unittest.TestCase):

    def test_no_win(self):
        """
        Test that the game is not one when all guesses are used up without a match
        :return:
        """
        game = WordleGame()
        game.game_state.solution = 'ABCDE'
        game.submit_guess("DEBUG", "Nobody")
        game.submit_guess("DEBUG", "Nobody")
        game.submit_guess("DEBUG", "Nobody")
        game.submit_guess("DEBUG", "Nobody")
        game.submit_guess("DEBUG", "Nobody")
        game.submit_guess("DEBUG", "Nobody")
        self.assertEqual(game.current_message, "Better luck next time")

    def test_bad_word(self):
        game = WordleGame()
        game.game_state.solution = 'ABCDE'
        game.submit_guess("XYZAB", "Nobody")
        self.assertEqual(game.current_message, "Not in word list\nTry again")

    def test_short_word(self):
        game = WordleGame()
        game.game_state.solution = 'ABCDE'
        game.submit_guess('ABC', "Nobody")
        self.assertEqual(game.current_message, "Word too short")
        game.submit_guess('ABCD', "Nobody")
        self.assertEqual(game.current_message, "Word too short")

    def Xtest_long_word(self):
        game = WordleGame()
        game.game_state.solution = 'ABCDE'
        game.submit_guess('ABCDEF', "Nobody")
        self.assertEqual(game.current_message, "Word too long")
        game.submit_guess('ABCDEFG', "Nobody")
        self.assertEqual(game.current_message, "Word too long")

    def test_partial_similarity(self):
        game = WordleGame()
        game.game_state.solution = 'DEBUG'
        game.submit_guess("BUGGY", "Nobody")
        self.assertEqual(game.game_state.board.board[0][0].letter, "B")
        self.assertEqual(game.game_state.board.board[0][0].color, wordle.YELLOW)
        self.assertEqual(game.game_state.board.board[0][1].letter, "U")
        self.assertEqual(game.game_state.board.board[0][1].color, wordle.YELLOW)
        self.assertEqual(game.game_state.board.board[0][2].letter, "G")
        self.assertEqual(game.game_state.board.board[0][2].color, wordle.YELLOW)
        self.assertEqual(game.game_state.board.board[0][3].letter, "G")
        self.assertEqual(game.game_state.board.board[0][3].color, wordle.GRAY)
        self.assertEqual(game.game_state.board.board[0][4].letter, "Y")
        self.assertEqual(game.game_state.board.board[0][4].color, wordle.GRAY)

    def test_all_similar(self):
        game = WordleGame()
        game.game_state.solution = 'STRTU'
        game.submit_guess("TRUST", "Nobody")  # only this needs to be a real word, solution can be made up
        self.assertEqual(game.game_state.board.board[0][0].letter, "T")
        self.assertEqual(game.game_state.board.board[0][0].color, wordle.YELLOW)
        self.assertEqual(game.game_state.board.board[0][1].letter, "R")
        self.assertEqual(game.game_state.board.board[0][1].color, wordle.YELLOW)
        self.assertEqual(game.game_state.board.board[0][2].letter, "U")
        self.assertEqual(game.game_state.board.board[0][2].color, wordle.YELLOW)
        self.assertEqual(game.game_state.board.board[0][3].letter, "S")
        self.assertEqual(game.game_state.board.board[0][3].color, wordle.YELLOW)
        self.assertEqual(game.game_state.board.board[0][4].letter, "T")
        self.assertEqual(game.game_state.board.board[0][4].color, wordle.YELLOW)

    def test_partial_match(self):
        game = WordleGame()
        game.game_state.solution = 'CRUST'
        game.submit_guess("TRUST", "Nobody")
        self.assertEqual(game.game_state.board.board[0][0].letter, "T")
        self.assertEqual(game.game_state.board.board[0][0].color, wordle.GRAY)
        self.assertEqual(game.game_state.board.board[0][1].letter, "R")
        self.assertEqual(game.game_state.board.board[0][1].color, wordle.GREEN)
        self.assertEqual(game.game_state.board.board[0][2].letter, "U")
        self.assertEqual(game.game_state.board.board[0][2].color, wordle.GREEN)
        self.assertEqual(game.game_state.board.board[0][3].letter, "S")
        self.assertEqual(game.game_state.board.board[0][3].color, wordle.GREEN)
        self.assertEqual(game.game_state.board.board[0][4].letter, "T")
        self.assertEqual(game.game_state.board.board[0][4].color, wordle.GREEN)

    def test_duplicates_in_solution(self):
        game = WordleGame()
        game.game_state.solution = 'LUPUS'
        game.submit_guess("LUMPS", "Nobody")
        self.assertEqual(game.game_state.board.board[0][0].letter, "L")
        self.assertEqual(game.game_state.board.board[0][0].color, wordle.GREEN)
        self.assertEqual(game.game_state.board.board[0][1].letter, "U")
        self.assertEqual(game.game_state.board.board[0][1].color, wordle.GREEN)
        self.assertEqual(game.game_state.board.board[0][2].letter, "M")
        self.assertEqual(game.game_state.board.board[0][2].color, wordle.GRAY)
        self.assertEqual(game.game_state.board.board[0][3].letter, "P")
        self.assertEqual(game.game_state.board.board[0][3].color, wordle.YELLOW)
        self.assertEqual(game.game_state.board.board[0][4].letter, "S")
        self.assertEqual(game.game_state.board.board[0][4].color, wordle.GREEN)

    def test_similar_duplicates_in_guess(self):
        game = WordleGame()
        game.game_state.solution = 'STARE'
        game.submit_guess("STEER", "Nobody")
        self.assertEqual(game.game_state.board.board[0][0].letter, "S")
        self.assertEqual(game.game_state.board.board[0][0].color, wordle.GREEN)
        self.assertEqual(game.game_state.board.board[0][1].letter, "T")
        self.assertEqual(game.game_state.board.board[0][1].color, wordle.GREEN)
        self.assertEqual(game.game_state.board.board[0][2].letter, "E")
        self.assertEqual(game.game_state.board.board[0][2].color, wordle.YELLOW)
        self.assertEqual(game.game_state.board.board[0][3].letter, "E")
        self.assertEqual(game.game_state.board.board[0][3].color, wordle.GRAY)
        self.assertEqual(game.game_state.board.board[0][4].letter, "R")
        self.assertEqual(game.game_state.board.board[0][4].color, wordle.YELLOW)

    def test_partial_match_duplicates_in_guess(self):
        # When the matched duplicate IS the first occurrence of the letter in the guess
        game = WordleGame()
        game.game_state.solution = 'PLUMP'
        game.submit_guess("PUPPY", "Nobody")
        self.assertEqual(game.game_state.board.board[0][0].letter, "P")
        self.assertEqual(game.game_state.board.board[0][0].color, wordle.GREEN)
        self.assertEqual(game.game_state.board.board[0][1].letter, "U")
        self.assertEqual(game.game_state.board.board[0][1].color, wordle.YELLOW)
        self.assertEqual(game.game_state.board.board[0][2].letter, "P")
        self.assertEqual(game.game_state.board.board[0][2].color, wordle.YELLOW)
        self.assertEqual(game.game_state.board.board[0][3].letter, "P")
        self.assertEqual(game.game_state.board.board[0][3].color, wordle.GRAY)
        self.assertEqual(game.game_state.board.board[0][4].letter, "Y")
        self.assertEqual(game.game_state.board.board[0][4].color, wordle.GRAY)

        # When the matched duplicate isn't the first occurrence of the letter in the guess
        game = WordleGame()
        game.game_state.solution = 'TARES'
        game.submit_guess("STEER", "Nobody")
        self.assertEqual(game.game_state.board.board[0][0].letter, "S")
        self.assertEqual(game.game_state.board.board[0][0].color, wordle.YELLOW)
        self.assertEqual(game.game_state.board.board[0][1].letter, "T")
        self.assertEqual(game.game_state.board.board[0][1].color, wordle.YELLOW)
        self.assertEqual(game.game_state.board.board[0][2].letter, "E")
        self.assertEqual(game.game_state.board.board[0][2].color, wordle.GRAY)
        self.assertEqual(game.game_state.board.board[0][3].letter, "E")
        self.assertEqual(game.game_state.board.board[0][3].color, wordle.GREEN)
        self.assertEqual(game.game_state.board.board[0][4].letter, "R")
        self.assertEqual(game.game_state.board.board[0][4].color, wordle.YELLOW)

        # When there are multiple matches
        game = WordleGame()
        game.game_state.solution = 'GUPPY'
        game.submit_guess("PUPPY", "Nobody")
        self.assertEqual(game.game_state.board.board[0][0].letter, "P")
        self.assertEqual(game.game_state.board.board[0][0].color, wordle.GRAY)
        self.assertEqual(game.game_state.board.board[0][1].letter, "U")
        self.assertEqual(game.game_state.board.board[0][1].color, wordle.GREEN)
        self.assertEqual(game.game_state.board.board[0][2].letter, "P")
        self.assertEqual(game.game_state.board.board[0][2].color, wordle.GREEN)
        self.assertEqual(game.game_state.board.board[0][3].letter, "P")
        self.assertEqual(game.game_state.board.board[0][3].color, wordle.GREEN)
        self.assertEqual(game.game_state.board.board[0][4].letter, "Y")
        self.assertEqual(game.game_state.board.board[0][4].color, wordle.GREEN)

        # Reverse of above case
        game = WordleGame()
        game.game_state.solution = 'PUPPY'
        game.submit_guess("GUPPY", "Nobody")
        self.assertEqual(game.game_state.board.board[0][0].letter, "G")
        self.assertEqual(game.game_state.board.board[0][0].color, wordle.GRAY)
        self.assertEqual(game.game_state.board.board[0][1].letter, "U")
        self.assertEqual(game.game_state.board.board[0][1].color, wordle.GREEN)
        self.assertEqual(game.game_state.board.board[0][2].letter, "P")
        self.assertEqual(game.game_state.board.board[0][2].color, wordle.GREEN)
        self.assertEqual(game.game_state.board.board[0][3].letter, "P")
        self.assertEqual(game.game_state.board.board[0][3].color, wordle.GREEN)
        self.assertEqual(game.game_state.board.board[0][4].letter, "Y")
        self.assertEqual(game.game_state.board.board[0][4].color, wordle.GREEN)

    def test_first_guess_win(self):
        game = WordleGame()
        game.game_state.solution = "FIRST"
        game.submit_guess("FIRST", "Nobody")
        self.assertEqual(game.game_state.is_over, True)
        self.assertEqual(game.current_message, "Nobody\nWins in 1!")

    def test_last_guess_win(self):
        game = WordleGame()
        game.game_state.solution = "SIXTH"
        game.submit_guess("FIRST", "Nobody")
        game.submit_guess("DEBUG", "Nobody")
        game.submit_guess("DEBUG", "Nobody")
        game.submit_guess("DEBUG", "Nobody")
        game.submit_guess("FIFTH", "Nobody")
        game.submit_guess("SIXTH", "Nobody")
        self.assertEqual(game.game_state.is_over, True)
        self.assertEqual(game.current_message, "Nobody\nWins in 6!")


if __name__ == '__main__':
    unittest.main()