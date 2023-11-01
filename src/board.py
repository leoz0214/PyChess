"""
Internal board implementation which is used by the display board.
Handles the logic of chess such as valid moves, checks and special moves
such as en passant, promotion and castling.
"""
from constants import FILES, RANKS
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
    
    def get(self, file: int, rank: int) -> "Square":
        """Returns the square at a particular file and rank."""
        return self.board[RANKS - rank - 1][file]

    def get_pawn_moves(
        self, square: "Square", colour: Colour
    ) -> list["Square"]:
        """The player selected a pawn, now get the possible moves."""
        forward_two = None
        if colour == Colour.WHITE:
            forward = self.get(square.file, square.rank + 1)
            if square.rank == 1:
                forward_two = self.get(square.file, square.rank + 2)
            if square.file > 0:
                left = self.get(square.file - 1, square.rank + 1)
            if square.file < FILES - 1:
                right = self.get(square.file + 1, square.rank + 1)
        else:
            forward = self.get(square.file, square.rank - 1)
            if square.rank == RANKS - 2:
                forward_two = self.get(square.file, square.rank - 2)
            if square.file < FILES - 1:
                left = self.get(square.file + 1, square.rank - 1)
            if square.file > 0:
                right = self.get(square.file - 1, square.rank - 1)
        moves = []
        if forward.empty:
            moves.append(forward)
        if forward_two is not None and forward_two.empty:
            moves.append(forward_two)
        for move in (left, right):
            if (not move.empty) and move.piece.colour != colour:
                moves.append(move)
        return moves


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

    @property
    def empty(self) -> bool:
        """No piece on the square currently."""
        return self.piece is None        
