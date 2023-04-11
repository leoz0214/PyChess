"""Utilities to be used throughout the game."""
import enum


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
