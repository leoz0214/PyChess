"""Utilities to be used throughout the game."""
import enum

import pygame as pg

from constants import INTER_FONT


class Colour(enum.Enum):
    """The two players in chess: White and Black."""
    # 0 represents white.
    WHITE = 0
    # 1 represents black.
    BLACK = 1


class Pieces(enum.Enum):
    """The various pieces in chess."""
    PAWN = "pawn"
    KNIGHT = "knight"
    BISHOP = "bishop"
    ROOK = "rook"
    QUEEN = "queen"
    KING = "king"


class Action(enum.Enum):
    """Possible navigation options when game is stopped."""
    RESTART = "restart"
    HOME = "home"


# Agreed values of each piece in terms of 'points'.
# The more points, the more valuable (powerful) a piece.
PIECE_POINTS = {
    Pieces.PAWN: 1,
    Pieces.KNIGHT: 3,
    Pieces.BISHOP: 3,
    Pieces.ROOK: 5,
    Pieces.QUEEN: 9
}

# Algebraic notation piece letters.
PIECE_LETTERS = {
    Pieces.KNIGHT: "N",
    Pieces.BISHOP: "B",
    Pieces.ROOK: "R",
    Pieces.QUEEN: "Q",
    Pieces.KING: "K"
}

# Files a - h
FILE_STRING = "abcdefgh"

OUTCOME_STRINGS = {
    Colour.WHITE: "1-0",
    Colour.BLACK: "0-1",
    None: "1/2-1/2"
}


def render_text(text: str, size: int, fg: str) -> pg.Surface:
    """Returns the text surface."""
    font = pg.font.Font(INTER_FONT, size)
    textbox = font.render(text, False, fg)
    return textbox


def in_rectangle(
    coordinates: tuple[int, int],
    top_left: tuple[int, int], bottom_right: tuple[int, int]
) -> bool:
    """Returns True if given coordinates lie in a rectangle else False."""
    x1, y1 = top_left
    x2, y2 = bottom_right
    return x1 <= coordinates[0] <= x2 and y1 <= coordinates[1] <= y2


def surface_clicked(
    surface: pg.Surface, x: int, y: int, coordinates: tuple[int, int],
    center: bool = True
) -> bool:
    """Returns True if a coordinate lies in a surface, else False."""
    width = surface.get_width()
    height = surface.get_height()
    if not center:
        left, top = x, y
    else:
        left, top = x - width // 2, y - height // 2
    return in_rectangle(coordinates, (left, top), (left + width, top + height))
