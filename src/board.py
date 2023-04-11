"""
Internal board implementation which is used by the display board.
Handles the logic of chess such as valid moves, checks and special moves
such as en passant, promotion and castling.
"""
from constants import FILES
from pieces import Piece, Pawn, Knight, Bishop, Rook, Queen, King
from utils import Colour


class Board:
    """Internal Chess board representation."""

    def __init__(self) -> None:
        back_rank = (Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook)
        self.board = [
            [Square(piece(Colour.BLACK)) for piece in back_rank],
            [Square(Pawn(Colour.BLACK)) for _ in range(FILES)],
            *[[Square() for _ in range(FILES)] for _ in range(4)],
            [Square(Pawn(Colour.WHITE)) for _ in range(FILES)],
            [Square(piece(Colour.WHITE)) for piece in back_rank]
        ]


class Square:
    """Internal Chess square representation."""

    def __init__(self, piece: Piece | None = None) -> None:
        self.piece = piece
