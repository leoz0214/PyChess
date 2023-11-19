"""Constants to be used throughout the program. Improves maintainability."""
import pathlib

import pygame as pg


# Window and program configuration.
WIDTH = 1000
HEIGHT = 600
TITLE = "PyChess"
FPS = 60

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

BOARD_MIN_X = 260
BOARD_MIN_Y = 50

RESULT_COLOUR = "#03a9fc"
RESULT_WIDTH = 300
RESULT_HEIGHT = 200

PROMOTION_COLOUR = "#03a9fc"
PROMOTION_WIDTH = 300
PROMOTION_HEIGHT = 125

OUTCOME_TEXT_SIZES = {
    "Checkmate": 50,
    "Stalemate": 50,
    "Fivefold Repetition": 30,
    "75 Move Rule": 40,
    "Insufficient Material": 30
}

INSIGNIFICANT_DRAG_RADIUS = 5

WHITE_MIN_X = 30
WHITE_MIN_Y = 50

BLACK_MIN_X = 770
BLACK_MIN_Y = 50

PLAYER_INFO_WIDTH = 200
PLAYER_INFO_HEIGHT = 450
PLAYER_INFO_FG = "#777777"

GAME_END_MIN_X = 260
GAME_END_MIN_Y = 540
GAME_END_WIDTH = 480
GAME_END_HEIGHT = 50

# Actual colours which can be displayed.
RED = "red"
WHITE = "white"
BLACK = "black"
GREY = "grey"
DARK_GREY = "#777777"

# Configuration
REVERSE_BOARD = False

# Directories and files.
GAME_DIR = pathlib.Path(__file__).parent.parent
FONT_DIR = GAME_DIR / "font"
INTER_FONT = FONT_DIR / "Inter.ttf"
PIECES_DIR = GAME_DIR / "pieces"
WHITE_PIECES_DIR = PIECES_DIR / "white"
BLACK_PIECES_DIR = PIECES_DIR / "black"

AUDIO_DIR = GAME_DIR / "audio"
# Sounds effects from chess.com.
CAPTURE_SFX = pg.mixer.Sound(AUDIO_DIR / "capture.mp3")
CASTLING_SFX = pg.mixer.Sound(AUDIO_DIR / "castling.mp3")
CHECK_SFX = pg.mixer.Sound(AUDIO_DIR / "check.mp3")
END_SFX = pg.mixer.Sound(AUDIO_DIR / "end.mp3")
MOVE_SFX = pg.mixer.Sound(AUDIO_DIR / "move.mp3")
PROMOTION_SFX = pg.mixer.Sound(AUDIO_DIR / "promotion.mp3")
START_SFX = pg.mixer.Sound(AUDIO_DIR / "start.mp3")
