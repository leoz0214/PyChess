"""
Internal board implementation which is used by the display board.
Handles the logic of chess such as valid moves, checks and special moves
such as en passant, promotion and castling.
"""
from itertools import product
from typing import Iterable

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
            *(
                [Square(file, rank) for file in range(FILES)]
                for rank in range(5, 1, -1)),
            [Square(file, 1, Pawn(Colour.WHITE)) for file in range(FILES)],
            [
                Square(file, 0, piece(Colour.WHITE))
                for file, piece in enumerate(back_rank)]
        ]
        self.turn = Colour.WHITE
    
    def get(self, file: int, rank: int) -> "Square":
        """Returns the square at a particular file and rank."""
        return self.board[RANKS - rank - 1][file]

    def get_pawn_moves(self, square: "Square") -> list["Square"]:
        """The player selected a pawn, now get the possible moves."""
        forward_two = None
        left = None
        right = None
        colour = self.turn
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
            if (
                move is not None
                and (not move.empty) and move.piece.colour != colour
            ):
                moves.append(move)
        return moves
    
    def get_knight_moves(self, square: "Square") -> list["Square"]:
        """The player selected a knight, now get the possible moves."""
        # Check all 8 possible moves to see if they are possible.
        moves = []
        colour = self.turn
        for file_shift, rank_shift in product((-2, -1, 1, 2), repeat=2):
            if abs(file_shift) == abs(rank_shift):
                # Diagonal, not L.
                continue
            file = square.file + file_shift
            rank = square.rank + rank_shift
            if not (0 <= file < FILES and 0 <= rank < RANKS):
                continue    
            move = self.get(file, rank)
            if move.empty or move.piece.colour != colour:
                moves.append(move)
        return moves
    
    def _get_straight_line_moves(
        self, square: "Square", iterable: Iterable,
        max_distance: int = FILES - 1
    ) -> list["Square"]:
        """
        For the bishop and rook, get all the possible moves by
        going as far as possible either horizontally/vertically (rook)
        or diagonally (bishop).
        """
        moves = []
        colour = self.turn
        for file_shift, rank_shift in iterable:
            for n in range(1, max_distance + 1):
                file = square.file + file_shift * n
                rank = square.rank + rank_shift * n
                if not (0 <= file < FILES and 0 <= rank < RANKS):
                    break
                move = self.get(file, rank)
                if move.empty:
                    moves.append(move)
                else:
                    if move.piece.colour != colour:
                        moves.append(move)
                    break
        return moves

    def get_bishop_moves(self, square: "Square") -> list["Square"]:
        """The player selected a bishop, now get the possible moves."""
        # Get moves in all 4 diagonals as far as possible.
        iterable = product((-1, 1), repeat=2)
        return self._get_straight_line_moves(square, iterable)

    def get_rook_moves(self, square: "Square") -> list["Square"]:
        """The player selected a rook, now get the possible moves."""
        # Get moves in a 4 directions as far as possible.
        # The file and rank shift combo must have exactly one 0.
        iterable = filter(
            lambda shifts: shifts.count(0) == 1, product((-1, 0, 1), repeat=2))
        return self._get_straight_line_moves(square, iterable)

    def get_queen_moves(self, square: "Square") -> list["Square"]:
        """The player selected a queen, now get the possible moves."""
        # The queen is a combined Bishop and Rook!
        return self.get_bishop_moves(square) + self.get_rook_moves(square)

    def get_king_moves(self, square: "Square") -> list["Square"]:
        """The player selected a king, now get the possible moves."""
        # As long as not both file and rank shifts are 0
        iterable = filter(
            lambda shifts: shifts.count(0) < 2, product((-1, 0, 1), repeat=2))
        # King can only travel one square in any direction.
        return self._get_straight_line_moves(square, iterable, max_distance=1)


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
