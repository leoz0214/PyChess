"""Constants to be used throughout the program. Improves maintainability."""
import pathlib


# Window and program configuration.
WIDTH = 1000
HEIGHT = 600
TITLE = "PyChess"
FPS = 30

# General chess board information.
RANKS = 8 # rows on a chess board.
FILES = 8 # columns on a chess board.

# Chess board and piece configuration for this program.
SQUARE_WIDTH = 60
DARK_SQUARE_COLOUR = "#736231"
LIGHT_SQUARE_COLOUR = "#e6ddc3"
PIECE_WIDTH = 55
SELECTED_SQUARE_COLOUR = "#03a9fc"
POSSIBLE_MOVE_CIRCLE_WIDTH = 10
POSSIBLE_MOVE_CIRCLE_COLOUR = "#888888"
BACKGROUND_COLOUR = "#8fc4cf"
RESULT_COLOUR = "#03a9fc"
BOARD_MIN_X = 260
BOARD_MIN_Y = 100
RESULT_WIDTH = 300
RESULT_HEIGHT = 200

# Actual colours which can be displayed.
RED = "red"
WHITE = "white"
BLACK = "black"
GREY = "grey"

# Configuration
REVERSE_BOARD = False

# Directories.
GAME_DIR = pathlib.Path(__file__).parent.parent
FONT_DIR = GAME_DIR / "font"
INTER_FONT = FONT_DIR / "Inter.ttf"
PIECES_DIR = GAME_DIR / "pieces"
WHITE_PIECES_DIR = PIECES_DIR / "white"
BLACK_PIECES_DIR = PIECES_DIR / "black"
