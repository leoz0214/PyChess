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
            [
                Square(file, 7, piece(Colour.BLACK))
                for file, piece in enumerate(back_rank)],
            [Square(file, 6, Pawn(Colour.BLACK)) for file in range(FILES)],
            *[
                [Square(file, rank) for file in range(FILES)]
                for rank in range(5, 1, -1)],
            [Square(file, 1, Pawn(Colour.WHITE)) for file in range(FILES)],
            [
                Square(file, 0, piece(Colour.WHITE))
                for file, piece in enumerate(back_rank)]
        ]
        self.turn = Colour.WHITE


class Square:
    """Internal Chess square representation."""

    def __init__(
        self, file: int, rank: int, piece: Piece | None = None
    ) -> None:
        self.file = file
        self.rank = rank
        self.piece = piece
    
    def __eq__(self, square: "Square") -> bool:
        return isinstance(square, Square) and self.__dict__ == square.__dict__
