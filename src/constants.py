"""Constants to be used throughout the program. Improves maintainability."""
import pathlib


# Window and program configuration.
WIDTH = 600
HEIGHT = 600
TITLE = "PyChess"
FPS = 30

# General chess board information.
RANKS = 8 # rows
FILES = 8 # columns

# Chess board and piece configuration for this program.
SQUARE_WIDTH = 60
DARK_SQUARE_COLOUR = "#736231"
LIGHT_SQUARE_COLOUR = "#e6ddc3"
PIECE_WIDTH = 55

# Directories.
PIECES_DIR = pathlib.Path(__file__).parent.parent / "pieces"
WHITE_PIECES_DIR = PIECES_DIR / "white"
BLACK_PIECES_DIR = PIECES_DIR / "black"
