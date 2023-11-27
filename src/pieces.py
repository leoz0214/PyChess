"""
Handles the chess pieces, including
pawns, knights, bishops, rooks, queens and kings.
"""
import io
import pygame as pg
from PIL import Image

from constants import (
    PIECE_WIDTH, SMALL_PIECE_WIDTH, WHITE_PIECES_DIR, BLACK_PIECES_DIR)
from utils import Colour, Pieces


def load_piece_image(
    colour: Colour, piece: Pieces, small: bool = False
) -> pg.Surface:
    """Loads a piece image by its colour and type."""
    directory = (WHITE_PIECES_DIR, BLACK_PIECES_DIR)[colour.value]
    file = directory / f"{piece.value}.png"
    width = SMALL_PIECE_WIDTH if small else PIECE_WIDTH
    image = Image.open(file).resize((width, width))
    with io.BytesIO() as f:
        image.save(f, "png")
        f.seek(0)
        return pg.image.load(f)


class Piece:
    """Parent class for the various chess pieces."""

    def __init__(
        self, colour: Colour, piece: Pieces, unique_letter: str, 
        promoted: bool = False
    ) -> None:
        self.colour = colour
        self.type = piece
        self.unique_letter = unique_letter
        self.image = load_piece_image(self.colour, self.type)
        self.promoted = promoted
    
    def __eq__(self, piece: "Piece") -> bool:
        return type(self) is type(piece) and self.__dict__ == piece.__dict__
    
    def __hash__(self) -> int:
        return id(self)

    def __repr__(self) -> str:
        """Unique representation for board state recordings."""
        return f"{self.unique_letter}{self.colour.value}"


class Pawn(Piece):
    """Represents a pawn (1 point value)."""

    def __init__(self, colour: Colour) -> None:
        super().__init__(colour, Pieces.PAWN, "p")


class Knight(Piece):
    """Represents a knight (3 points value)."""

    def __init__(self, colour: Colour, promoted: bool = False) -> None:
        super().__init__(colour, Pieces.KNIGHT, "n", promoted)


class Bishop(Piece):
    """Represents a bishop (3 points value)."""

    def __init__(self, colour: Colour, promoted: bool = False) -> None:
        super().__init__(colour, Pieces.BISHOP, "b", promoted)


class Rook(Piece):
    """Represents a rook (5 points value)."""

    def __init__(self, colour: Colour, promoted: bool = False) -> None:
        super().__init__(colour, Pieces.ROOK, "r", promoted)


class Queen(Piece):
    """Represents a queen (9 points value)."""

    def __init__(self, colour: Colour, promoted: bool = False) -> None:
        super().__init__(colour, Pieces.QUEEN, "q", promoted)


class King(Piece):
    """Represents a king (utmost importance)."""

    def __init__(self, colour: Colour) -> None:
        super().__init__(colour, Pieces.KING, "k")
