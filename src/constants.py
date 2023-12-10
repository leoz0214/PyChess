"""Constants to be used throughout the program. Improves maintainability."""
import pathlib
import sys

import pygame as pg


# Window and program configuration.
WIDTH = 1000
HEIGHT = 600
TITLE = "PyChess"
FPS = 60

# Home screen configuration
HOME_SCREEN_FG = "#777777"
TIME_CONTROLS_MIN_X = 200
TIME_CONTROLS_MIN_Y = 150
TIME_CONTROLS_WIDTH = 600
TIME_CONTROLS_HEIGHT = 150
SELECTED_TIME_CONTROL_COLOUR = "#03a9fc"

# Fixed time controls. Format: (seconds, added seconds / move): display
TIME_CONTROLS = {
    (float("inf"), 0): "None",
    (30, 0): "30 sec",
    (60, 0): "1 min",
    (180, 0): "3 min",
    (300, 0): "5 min",
    (600, 0): "10 min",
    (1800, 0): "30 min",
    (3600, 0): "60 min",
    (5400, 0): "90 min",
    (7200, 0): "2 hr",
    (60, 1): "1 | 1",
    (120, 1): "2 | 1",
    (180, 2): "3 | 2",
    (300, 5): "5 | 5",
    (900, 10): "15 | 10"
}
TIME_CONTROL_WIDTH = 85
TIME_CONTROL_HEIGHT = 27
TIME_CONTROLS_PER_ROW = 5

# Game settings section.
SETTINGS_MIN_X = 200
SETTINGS_MIN_Y = 325
SETTINGS_WIDTH = 600
SETTINGS_HEIGHT = 150
SELECTED_SETTING_COLOUR = "#03a9fc"
# Setting identifiers and the display prompt.
SETTINGS = {
    "reverse": ("Automatically flip board", True)
}
SETTING_WIDTH = 350
SETTING_HEIGHT = 30

# General chess board information.
RANKS = 8 # rows on a chess board.
FILES = 8 # columns on a chess board.

# Chess board and piece configuration for this program.
SQUARE_WIDTH = 60
DARK_SQUARE_COLOUR = "#736231"
LIGHT_SQUARE_COLOUR = "#e6ddc3"
PIECE_WIDTH = 55
SELECTED_SQUARE_COLOUR = "#03a9fc"

# The circle that appears on a square which can be moved to.
POSSIBLE_MOVE_CIRCLE_WIDTH = 10
POSSIBLE_MOVE_CIRCLE_COLOUR = "#888888"

BACKGROUND_COLOUR = "#8fc4cf"

# Board top-level coordinates
BOARD_MIN_X = 260
BOARD_MIN_Y = 50

# Result popup config.
RESULT_COLOUR = "#03a9fc"
RESULT_WIDTH = 300
RESULT_HEIGHT = 200

# Promotion menu popup config.
PROMOTION_COLOUR = "#03a9fc"
PROMOTION_WIDTH = 300
PROMOTION_HEIGHT = 125

# The possible outcome texts and the corresponding font sizes.
# Obviously, the longer the text, the smaller the font.
OUTCOME_TEXT_SIZES = {
    "Checkmate": 50,
    "Stalemate": 50,
    "Fivefold Repetition": 30,
    "Threefold Repetition": 30,
    "75 Move Rule": 40,
    "50 Move Rule": 40,
    "Insufficient Material": 30,
    "Resignation": 50,
    "Mutual": 50,
    "Timeout": 50,
    "Timeout vs Insufficient Material": 20
}

# How many pixels of mouse drag can be ignored.
INSIGNIFICANT_DRAG_RADIUS = 5

# Colour info display config.
WHITE_MIN_X = 30
WHITE_MIN_Y = 50

BLACK_MIN_X = 770
BLACK_MIN_Y = 50

PLAYER_INFO_WIDTH = 200
PLAYER_INFO_HEIGHT = 450
PLAYER_INFO_FG = "#777777"

# Game options bottom menu config.
GAME_OPTIONS_MIN_X = 260
GAME_OPTIONS_MIN_Y = 540
GAME_OPTIONS_WIDTH = 480
GAME_OPTIONS_HEIGHT = 50

# Captured pieces display.
CAPTURED_PIECES_PER_ROW = 8
CAPTURED_PIECES_WIDTH = 175
CAPTURED_PIECES_HEIGHT = 50
SMALL_PIECE_WIDTH = 25
SMALL_PIECE_OVERLAP = 5

PGN_FG = "#777777"

# Actual colours which can be displayed.
RED = "red"
WHITE = "white"
BLACK = "black"
GREY = "grey"
DARK_GREY = "#777777"

# Directories and files.
if hasattr(sys, "_MEIPASS"):
    # From executable.
    GAME_DIR = pathlib.Path(sys._MEIPASS)
else:
    # From Python.
    GAME_DIR = pathlib.Path(__file__).parent.parent

# Game font
FONT_DIR = GAME_DIR / "font"
INTER_FONT = FONT_DIR / "Inter.ttf"

# Image handling including pieces.
IMAGES_DIR = GAME_DIR / "images"
PIECES_DIR = IMAGES_DIR / "pieces"
WHITE_PIECES_DIR = PIECES_DIR / "white"
BLACK_PIECES_DIR = PIECES_DIR / "black"
ICON = IMAGES_DIR / "icon.ico"

AUDIO_DIR = GAME_DIR / "audio"
# Sounds effects from chess.com.
CAPTURE_SFX = pg.mixer.Sound(AUDIO_DIR / "capture.mp3")
CASTLING_SFX = pg.mixer.Sound(AUDIO_DIR / "castling.mp3")
CHECK_SFX = pg.mixer.Sound(AUDIO_DIR / "check.mp3")
END_SFX = pg.mixer.Sound(AUDIO_DIR / "end.mp3")
MOVE_SFX = pg.mixer.Sound(AUDIO_DIR / "move.mp3")
PROMOTION_SFX = pg.mixer.Sound(AUDIO_DIR / "promotion.mp3")
START_SFX = pg.mixer.Sound(AUDIO_DIR / "start.mp3")
