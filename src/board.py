"""
Internal board implementation which is used by the display board.
Handles the logic of chess such as valid moves, checks and special moves
such as en passant, promotion and castling.
"""
from copy import copy
from dataclasses import dataclass
from itertools import product
from typing import Iterable, Union

from constants import FILES, RANKS
from pieces import Piece, Pawn, Knight, Bishop, Rook, Queen, King
from utils import Colour, Pieces


@dataclass
class Move:
    """
    Stores the source square and destination square of a played move, along with
    any special attributes: castle, en passant, etc.
    """
    # State of the two squares before the move.
    from_before: "Square"
    to_before: "Square"
    # State of the two squares after the move.
    from_after: "Square"
    to_after: "Square"
    # Special attributes.
    castle: bool = False
    en_passant: bool = False
    promotion: bool = False


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
        # Performing a test move at the moment.
        self.test_move = False
        self.moves = []
        self.move_methods = {
            Pieces.PAWN: self.get_pawn_moves,
            Pieces.KNIGHT: self.get_knight_moves,
            Pieces.BISHOP: self.get_bishop_moves,
            Pieces.ROOK: self.get_rook_moves,
            Pieces.QUEEN: self.get_queen_moves,
            Pieces.KING: self.get_king_moves
        }
    
    @property
    def opponent(self) -> Colour:
        """The opposing colour relative to the current turn."""
        # Index 0 (white -> black), Index 1 (black -> white)
        return (Colour.BLACK, Colour.WHITE)[self.turn.value]
    
    @property
    def checkmate_square(self) -> Union["Square", None]:
        """Returns the square of the checkmated king, else None."""
        self.test_move = True
        possible_next_squares = self.get_all_moves()
        king_square = None
        for file in range(FILES):
            for rank in range(RANKS):
                square = self.get(file, rank)
                if (
                    (not square.empty) and square.piece.type == Pieces.KING
                    and square.piece.colour != self.turn
                ):
                    king_square = square
                    break
            if king_square is not None:
                break
        king_attacked = king_square in possible_next_squares
        self.test_move = False
        if not king_attacked:
            return None
        self.invert_turn()
        is_checkmate = not self.get_all_moves()
        self.invert_turn()
        return king_square if is_checkmate else None
    
    def get(self, file: int, rank: int) -> "Square":
        """Returns the square at a particular file and rank."""
        return self.board[RANKS - rank - 1][file]

    def invert_turn(self) -> None:
        """Changes the turn to white or black now."""
        # Index 0 (white -> black), Index 1 (black -> white)
        self.turn = self.opponent
    
    def add_move(
        self, from_before: "Square", to_before: "Square",
        from_after: "Square", to_after: "Square", is_en_passant: bool,
        is_promotion: bool
    ) -> None:
        """Adds a move to the list of moves in the game."""
        move = Move(
            from_before, to_before, from_after, to_after,
            en_passant=is_en_passant, promotion=is_promotion)
        self.moves.append(move)
    
    def legal_move(self, square: "Square", move: "Square") -> bool:
        """
        Checks a move is legal (does not lead to King capture).
        Note: treat pawn promotion as a normal pawn move. It does
        not matter what the pawn promotes to as this will not
        affect the legality of the move.
        """
        is_en_passant = self.is_en_passant(square, move)
        if is_en_passant:
            en_passant_victim = self.get(move.file, square.rank)
            en_passant_piece = en_passant_victim.piece
            en_passant_victim.piece = None
    
        # Simulate move and see the consequence.
        original_piece = square.piece
        square.piece = None

        original_move_piece = move.piece
        move.piece = original_piece
        self.invert_turn()
        self.test_move = True
        opponent_moves = self.get_all_moves()
        is_legal = all(
            opponent_move.empty or opponent_move.piece.type != Pieces.KING         
            for opponent_move in opponent_moves)

        square.piece = original_piece
        move.piece = original_move_piece
        if is_en_passant:
            en_passant_victim.piece = en_passant_piece
        self.invert_turn()
        self.test_move = False
        
        return is_legal

    def is_en_passant(self, square: "Square", move: "Square") -> bool:
        """Check if a move is valid en passant."""
        if square.piece.type != Pieces.PAWN or not self.moves:
            return False
        rank = RANKS - 3 - 1 if self.turn == Colour.WHITE else 3
        if square.rank != rank:
            return False
        previous_move = self.moves[-1]
        return (
            previous_move.from_before.piece.type == Pieces.PAWN
            and previous_move.from_before.file == move.file
            and abs(previous_move.from_before.rank - rank) == 2)

    def is_promotion(self, square: "Square", move: "Square") -> bool:
        """Check if a move is a pawn promotion."""
        return (
            square.piece.type == Pieces.PAWN and move.rank in (0, RANKS - 1))
    
    def filter_possible_moves(
        self, square: "Square", moves: list["Square"]
    ) -> list["Square"]:
        """
        Removes any moves which cannot be played due
        to exposing the King to checkmate.
        """
        if self.test_move:
            # Came from the test for a legal move.
            # Meaning the current colour's king is safe even if exposed
            # since the other king will be doomed first. Allow for
            # all moves no matter the current king's safety.
            return moves
        return [move for move in moves if self.legal_move(square, move)]

    def get_pawn_moves(self, square: "Square") -> list["Square"]:
        """The player selected a pawn, now get the possible moves."""
        forward_two = None
        left = None
        right = None
        if self.turn == Colour.WHITE:
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
                and (
                    (not move.empty) and move.piece.colour != self.turn
                    or self.is_en_passant(square, move)
                )
            ):
                moves.append(move)
        return self.filter_possible_moves(square, moves)
    
    def get_knight_moves(self, square: "Square") -> list["Square"]:
        """The player selected a knight, now get the possible moves."""
        # Check all 8 possible moves to see if they are possible.
        moves = []
        for file_shift, rank_shift in product((-2, -1, 1, 2), repeat=2):
            if abs(file_shift) == abs(rank_shift):
                # Diagonal, not L.
                continue
            file = square.file + file_shift
            rank = square.rank + rank_shift
            if not (0 <= file < FILES and 0 <= rank < RANKS):
                continue    
            move = self.get(file, rank)
            if move.empty or move.piece.colour != self.turn:
                moves.append(move)
        return self.filter_possible_moves(square, moves)
    
    def _get_straight_line_moves(
        self, square: "Square", iterable: Iterable,
        max_distance: int = FILES - 1
    ) -> list["Square"]:
        """
        For the bishop/rook/king, get all the possible moves by
        going as far as possible either horizontally/vertically (rook)
        or diagonally (bishop), or surround (king).
        """
        moves = []
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
                    if move.piece.colour != self.turn:
                        moves.append(move)
                    break
        return self.filter_possible_moves(square, moves)

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
        # The queen can be considered a combined Bishop and Rook!
        return self.get_bishop_moves(square) + self.get_rook_moves(square)

    def get_king_moves(self, square: "Square") -> list["Square"]:
        """The player selected a king, now get the possible moves."""
        # As long as NOT both file and rank shifts are 0
        iterable = filter(
            lambda shifts: shifts.count(0) < 2, product((-1, 0, 1), repeat=2))
        # King can only travel one square in any direction.
        return self._get_straight_line_moves(square, iterable, max_distance=1)

    def get_all_moves(self) -> list["Square"]:
        """
        Returns all possible moves which can be made by the current player.
        All pieces are checked.
        """
        moves = []
        for file in range(FILES):
            for rank in range(RANKS):
                square = self.get(file, rank)
                if (not square.empty) and square.piece.colour == self.turn:
                    piece_moves = self.move_methods[square.piece.type](square)
                    moves.extend(piece_moves)
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

    def copy(self) -> "Square":
        """
        Returns a copy of the square.
        Note, the piece remains the same object.
        """
        return copy(self)
