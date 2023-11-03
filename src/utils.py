"""Utilities to be used throughout the game."""
import enum

import pygame as pg

from constants import INTER_FONT


class Colour(enum.Enum):
    """The two players in chess: White and Black."""
    WHITE = 0
    BLACK = 1


class Pieces(enum.Enum):
    """The various pieces in chess."""
    PAWN = "pawn"
    KNIGHT = "knight"
    BISHOP = "bishop"
    ROOK = "rook"
    QUEEN = "queen"
    KING = "king"


def render_text(text: str, size: int, fg: str) -> pg.Surface:
    """Returns the text surface."""
    font = pg.font.Font(INTER_FONT, size)
    textbox = font.render(text, False, fg)
    return textbox


def surface_clicked(
    surface: pg.Surface, x: int, y: int, coordinates: tuple[int, int],
    center: bool = True
) -> bool:
    """Returns True if a coordinate lies in a surface, else False."""
    click_x, click_y = coordinates
    width = surface.get_width()
    height = surface.get_height()
    if not center:
        left, top = x, y
    else:
        left, top = x - width // 2, y - height // 2
    return left <= click_x <= left + width and top <= click_y <= top + height
