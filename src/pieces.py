"""
Handles the chess pieces, including
pawns, knights, bishops, rooks, queens and kings.
"""
import pygame as pg
from PIL import Image

from constants import PIECE_WIDTH, WHITE_PIECES_DIR, BLACK_PIECES_DIR
from utils import Colour, Pieces


def load_piece_image(colour: Colour, piece: Pieces) -> pg.Surface:
    """Loads a piece image by its colour and type."""
    directory = (
        WHITE_PIECES_DIR if colour == Colour.WHITE else BLACK_PIECES_DIR)
    file = directory / f"{piece.value}.png"
    image = Image.open(file).resize((PIECE_WIDTH, PIECE_WIDTH))
    with file.open("wb") as f:
        image.save(f, "png")
    return pg.image.load(file)


class Piece:
    """Parent class for the various chess pieces."""

    def __init__(self, colour: Colour, piece: pg.Surface) -> None:
        self.colour = colour
        self.type = piece
        self.image = load_piece_image(self.colour, self.type)
    
    def __eq__(self, piece: "Piece") -> bool:
        return type(self) is type(piece) and self.__dict__ == piece.__dict__


class Pawn(Piece):
    """Represents a pawn (1 point value)."""

    def __init__(self, colour: Colour) -> None:
        super().__init__(colour, Pieces.PAWN)


class Knight(Piece):
    """Represents a knight (3 points value)."""

    def __init__(self, colour: Colour) -> None:
        super().__init__(colour, Pieces.KNIGHT)


class Bishop(Piece):
    """Represents a bishop (3 points value)."""

    def __init__(self, colour: Colour) -> None:
        super().__init__(colour, Pieces.BISHOP)


class Rook(Piece):
    """Represents a rook (5 points value)."""

    def __init__(self, colour: Colour) -> None:
        super().__init__(colour, Pieces.ROOK)


class Queen(Piece):
    """Represents a queen (9 points value)."""

    def __init__(self, colour: Colour) -> None:
        super().__init__(colour, Pieces.QUEEN)


class King(Piece):
    """Represents a king (utmost importance)."""

    def __init__(self, colour: Colour) -> None:
        super().__init__(colour, Pieces.KING)
