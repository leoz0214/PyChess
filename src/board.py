"""
Internal board implementation which is used by the display board.
Handles the logic of chess such as valid moves, checks and special moves
such as en passant, promotion and castling.
"""
from copy import copy
from dataclasses import dataclass
from hashlib import sha256
from itertools import product
from typing import Iterable, Union

from constants import FILES, RANKS
from pieces import Piece, Pawn, Knight, Bishop, Rook, Queen, King
from utils import Colour, Pieces, PIECE_POINTS


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
    castling: bool = False
    en_passant: bool = False
    promotion: bool = False


@dataclass
class _MoveData:
    """Utilities for handling dummy moves internally. Not for general use."""
    square_piece: Piece | None
    move_piece: Piece | None
    position_counts: dict[str, int]


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
        # Moves which have been played by both colours.
        self.moves = []
        self.move_methods = {
            Pieces.PAWN: self.get_pawn_moves,
            Pieces.KNIGHT: self.get_knight_moves,
            Pieces.BISHOP: self.get_bishop_moves,
            Pieces.ROOK: self.get_rook_moves,
            Pieces.QUEEN: self.get_queen_moves,
            Pieces.KING: self.get_king_moves
        }
        # Captures which have been made.
        self.captured = {
            colour: dict.fromkeys(
                (Pieces.PAWN, Pieces.KNIGHT,
                    Pieces.BISHOP, Pieces.ROOK, Pieces.QUEEN), 0)
            for colour in (Colour.WHITE, Colour.BLACK)
        }
        # Current total pieces points.
        self.piece_points = {}
        self.set_piece_points()
        # Tracks the number of times unique positions have been seen
        # to allow for n-fold repetition detection.
        self.position_counts = {}
        self.set_moves()
    
    @property
    def opponent(self) -> Colour:
        """The opposing colour relative to the current turn."""
        # Index 0 (white -> black), Index 1 (black -> white)
        return (Colour.BLACK, Colour.WHITE)[self.turn.value]

    @property
    def is_check(self) -> bool:
        """Returns if the king is in check right now."""
        king_square = self.get_king_square()
        self.test_move = True
        self.invert_turn()
        opponent_moves = self.get_all_moves()
        self.test_move = False
        self.invert_turn()
        return king_square in opponent_moves
    
    @property
    def checkmate_square(self) -> Union["Square", None]:
        """Returns the square of the checkmated king, else None."""
        self.test_move = True
        possible_next_squares = self.get_all_moves()
        self.test_move = False
        king_square = self.get_king_square(opponent=True)
        king_attacked = king_square in possible_next_squares
        if not king_attacked:
            return None
        self.invert_turn()
        is_checkmate = not self.get_all_moves()
        self.invert_turn()
        return king_square if is_checkmate else None
    
    def __iter__(self) -> None:
        """
        Iterates through every square from rank 1,
        file a all the way to rank 8, file h.
        """
        for file, rank in product(range(FILES), range(RANKS)):
            yield self.get(file, rank)

    def get_king_square(self, opponent: bool = False) -> "Square":
        """Identifies the king square of the current/opponent colour."""
        for square in self:
            if (
                (not square.empty) and square.piece.type == Pieces.KING
                and (square.piece.colour != self.turn) == opponent
            ):
                return square
    
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
        is_promotion: bool, is_castling: bool
    ) -> None:
        """Adds a move to the list of moves in the game."""
        move = Move(
            from_before, to_before, from_after, to_after,
            is_castling, is_en_passant, is_promotion)
        self.moves.append(move)
    
    def add_capture(self, piece: Piece) -> None:
        """Registers a piece to have been captured."""
        piece_type = piece.type if not piece.promoted else Pieces.PAWN
        self.captured[piece.colour][piece_type] += 1
    
    def legal_move(self, square: "Square", move: "Square") -> bool:
        """
        Checks a move is legal (does not lead to King capture).
        Note: treat pawn promotion as a normal pawn move. It does
        not matter what the pawn promotes to as this will not
        affect the legality of the move.
        """
        is_en_passant = self.is_en_passant(square, move)
        is_castling = self.is_castling(square, move, validate=False)
        if is_en_passant:
            en_passant_victim = self.get(move.file, square.rank)
            en_passant_piece = en_passant_victim.piece
            en_passant_victim.piece = None
        if is_castling:
            kingside = move.file == 6
            rook_square = self.get(FILES - 1 if kingside else 0, square.rank)
            rook = rook_square.piece
            rook_square.piece = None
    
        # Simulate move and see the consequence.
        original_piece = square.piece
        square.piece = None

        original_move_piece = move.piece
        move.piece = original_piece

        if is_castling:
            # Also move the rook accordingly.
            new_rook_square = self.get(5 if kingside else 3, square.rank)
            new_rook_square.piece = rook

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
        if is_castling:
            rook_square.piece = rook
            new_rook_square.piece = None

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
            and previous_move.to_before.rank == rank
            and abs(previous_move.from_before.rank
                - previous_move.to_before.rank) == 2)

    def is_promotion(self, square: "Square", move: "Square") -> bool:
        """Check if a move is a pawn promotion."""
        return (
            square.piece.type == Pieces.PAWN and move.rank in (0, RANKS - 1))
    
    def is_castling(
        self, square: "Square", move: "Square", validate: bool = True
    ) -> bool:
        """Check if a move is a valid castling move."""
        if not (
            square.piece.type == Pieces.KING
            and abs(move.file - square.file) == 2
        ):
            return False
        if not validate:
            return True
        kingside = move.file == 6
        rook_square = self.get(FILES - 1 if kingside else 0, square.rank)
        if (
            rook_square.empty or rook_square.piece.type != Pieces.ROOK
            or rook_square.piece.colour != self.turn
        ):
            return False
        king = square.piece
        rook = rook_square.piece
        # Confirms the king and rook have not moved.
        if any(
            played_move.from_before.piece in (king, rook)
            for played_move in self.moves[self.turn.value::2]
        ):
            return False
        # Confirms all squares between king and rook are empty.
        file_range = range(5, FILES - 1) if kingside else range(1, 4)
        if any(
            not self.get(file, square.rank).empty for file in file_range
        ):
            return False
        # Confirms King is not in check and none of the square between
        # the king and castle position are attacked by the opponent.
        file_range = range(4, 6) if kingside else range(3, 5)
        squares = [self.get(file, square.rank) for file in file_range]
        return not self.any_square_under_attack(squares)

    def any_square_under_attack(self, squares: list["Square"]) -> bool:
        """
        Check if any squares out of a
        given list are under attack by the opponent.
        Remember, pinned opponent pieces can still attack.
        """
        self.test_move = True
        self.invert_turn()
        opponent_moves = self.get_all_moves()
        attacked = any(square in opponent_moves for square in squares)
        self.test_move = False
        self.invert_turn()
        return attacked
    
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

    def is_nfold_repetition(self, n: int) -> bool:
        """Returns if n-fold repetition has been attained."""
        return max(self.position_counts.values()) >= n

    def record_position(self) -> None:
        """
        Records the current board state fully,
        including pieces, possible moves and turns, adding to a counter.
        """
        state = [self.turn.value]
        # Add board state.
        for square in self:
            state.append(None if square.empty else repr(square.piece))
        # Add possible moves. This accounts for en passant/castling rights.
        for piece, moves in self.current_moves.items():
            piece_move_state = (repr(piece),) + tuple(
                (move.file, move.rank) for move in moves)
            state.append(piece_move_state)
        # Store hash to reduce memory consumption
        # (do not need to know actual position).
        hash_ = sha256(str(state).encode(), usedforsecurity=False).hexdigest()
        self.position_counts[hash_] = self.position_counts.get(hash_, 0) + 1
    
    def is_nmove_rule(self, n: int) -> bool:
        """
        Returns True if n moves have passed
        without a pawn move or capture by either player.
        In this context, a move is defined as a player completing
        their turn followed by the opponent also completing their turn.
        So the last 2n moves will be checked, and also,
        number of moves >= 2n for True. 
        """
        if len(self.moves) < n * 2:
            return False
        to_check = self.moves[-n * 2:]
        return all(
            move.from_before.piece.type != Pieces.PAWN
            and move.to_before.empty for move in to_check)
    
    @property
    def is_insufficient_material(self) -> bool:
        """
        Performs a basic check to see if there is no possible checkmate.
        Combinations with insufficient material to checkmate include:
        - King vs King
        - King and bishop vs king
        - King and knight vs king
        - King and bishop vs king and bishop, bishops on the same colour.
        """
        counts = {}
        bishop_squares = {Colour.WHITE: None, Colour.BLACK: None}
        for colour in (Colour.WHITE, Colour.BLACK):
            colour_counts = {}
            for square in self:
                if (not square.empty) and square.piece.colour == colour:
                    if (
                        square.piece.type in
                            (Pieces.PAWN, Pieces.ROOK, Pieces.QUEEN)
                    ):
                        # A pawn suggests a possible checkmate (despite not
                        # guaranteed, will be fine for this simple check).
                        # A single rook/queen guarantees a possible checkmate.
                        return False
                    colour_counts[square.piece.type] = (
                        colour_counts.get(square.piece.type, 0) + 1)
                    if square.piece.type == Pieces.BISHOP:
                        # Only record one square, since 2 or more bishops
                        # will indeed allow for a possible checkmate so
                        # the bishop squares will no longer matter
                        # (only to check both bishops are dark/light).
                        bishop_squares[colour] = square
            counts[colour] = colour_counts
        for colour, colour_counts in counts.items():
            colour_pieces = sum(colour_counts.values())
            opponent_counts = counts[
                (Colour.WHITE, Colour.BLACK)[not colour.value]]
            opponent_pieces = sum(opponent_counts.values())
            if opponent_pieces == 1:
                # Opponent only has one piece - king.
                if colour_pieces <= 2:
                    # If 1, Current player also only has one piece - king.
                    # King + King = Insufficient.
                    # If 2, King + One Knight OR Bishop = Insufficient.
                    return True
            if (
                colour_pieces == 2
                and colour_counts.get(Pieces.BISHOP) == 1
                and opponent_pieces == 2
                and opponent_counts.get(Pieces.BISHOP) == 1
            ):
                # Opponent has king and bishop.
                is_dark = [
                    square.file % 2 == square.rank % 2
                    for square in bishop_squares.values()]
                if is_dark[0] == is_dark[1]:
                    # Bishops same colour. Checkmate not possible.
                    return True
        # No evidence of impossible checkmate. Consider the game to
        # be in a playable state, continuing it.
        return False

    def _make_move(
        self, square: "Square", move: "Move",
        promotion_piece: Piece | None = None
    ) -> _MoveData:
        """
        Internal make move function for forward testing.
        Note, can ignore en passant possibility since opponent
        has no pawns, otherwise not insufficent material anyways.
        Also can ignore castling due to it being impossible to
        go from castling to instant mate when opponent only has
        1 knight or bishop.
        Also, for opponent, only king/knight/bishop, so again,
        no en passant/castle possibility.
        """
        is_promotion = promotion_piece is not None
        square_before = square.copy()
        square_piece = square.piece
        square.piece = None
        square_after = square.copy()

        move_before = move.copy()
        move_piece = move.piece
        move.piece = (
            square_piece if not is_promotion
            else promotion_piece(self.turn, promoted=True))
        move_after = move.copy()

        # Obtain current position counts.
        position_counts = self.position_counts.copy()
        # Record position counts to handle 5 fold reptition (very unlikely).
        self.record_position()

        self.add_move(
            square_before, move_before, square_after, move_after,
            False, is_promotion, False)
        
        return _MoveData(square_piece, move_piece, position_counts)

    def _undo_move(
        self, src: "Square", dest: "Square", move_data: _MoveData
    ) -> None:
        """Undos a dummy move."""
        src.piece = move_data.square_piece
        dest.piece = move_data.move_piece
        self.position_counts = move_data.position_counts
        self.moves.pop()

    @property
    def is_timeout_vs_insufficient_material(self) -> bool:
        """
        Performs a basic check to see if a timeout vs insufficient
        material has arisen, where the current player has run out of
        time but the opponent cannot deliver checkmate.
        Timeout vs insufficient material scenarios:
        - Only King left
        - King and only 1 Knight left
        - King and only 1 Bishop left.
        Rare cases may mean 1 Knight/Bishop suffices still.
        """
        count = 0
        colour = (Colour.WHITE, Colour.BLACK)[not self.turn.value]
        for square in self:
            if (not square.empty) and square.piece.colour == colour:
                if square.piece.type in (
                    Pieces.PAWN, Pieces.ROOK, Pieces.QUEEN
                ):
                    # A single pawn, rook or queen means not insufficient.
                    return False
                count += 1
                if count == 3:
                    # King and 2 knights/bishops OR 3 knights/bishops.
                    # Either way not insufficient.
                    return False
        # Count 2 or less. King + only one bishop/knight. Insufficient.
        # Unless there is somehow indeed a mate.
        insuffient = True
        for square in self:
            if square.piece not in self.current_moves:
                continue
            moves = self.current_moves[square.piece]
            # Simulates a move to see if any subsequent mates are possible.
            for move in moves:
                is_promotion = self.is_promotion(square, move)
                promotion_pieces = (None,) if not is_promotion else (
                    Knight, Bishop, Rook, Queen)
                for promotion_piece in promotion_pieces:
                    move_data = self._make_move(square, move, promotion_piece)
                    self.invert_turn()
                    # Checks move does not trigger 5-fold repetition or 75 move rule.
                    if not (
                        self.is_nfold_repetition(5) or self.is_nmove_rule(75)
                    ):
                        opponent_moves = self.get_moves()
                        for square_ in self:
                            # King/irrelevant piece ignored (cannot mate).
                            if (
                                square_.piece not in opponent_moves
                                or square_.piece.type == Pieces.KING
                            ):
                                continue
                            moves_ = opponent_moves[square_.piece]
                            for move_ in moves_:
                                move_data_ = self._make_move(square_, move_)
                                if self.checkmate_square is not None:
                                    insuffient = False
                                self._undo_move(square_, move_, move_data_)
                                if not insuffient:
                                    break
                    self._undo_move(square, move, move_data)
                    self.invert_turn()
                    if not insuffient:
                        return False
        # No simple checkmates found.
        return True

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
        moves = self._get_straight_line_moves(square, iterable, max_distance=1)
        backrank = 0 if self.turn == Colour.WHITE else RANKS - 1
        if square.file == 4 and square.rank == backrank and not self.test_move:
            # Also check castling, provided King is at starting square
            # and also the move is not a test move.
            kingside_castle = self.get(6, backrank)
            queenside_castle = self.get(2, backrank)
            for move in (kingside_castle, queenside_castle):
                if (
                    self.is_castling(square, move)
                    and self.legal_move(square, move)
                ):
                    moves.append(move)
        return moves       

    def get_all_moves(self) -> list["Square"]:
        """
        Returns all possible moves which can be made by the current player.
        All pieces are checked.
        """
        moves = []
        for square in self:
            if (not square.empty) and square.piece.colour == self.turn:
                piece_moves = self.move_methods[square.piece.type](square)
                moves.extend(piece_moves)
        return moves

    def get_moves(self) -> dict[Piece, list["Square"]]:
        """Gets all possible moves for all pieces."""
        moves = {}
        for square in self:
            if (not square.empty) and square.piece.colour == self.turn:
                piece_moves = self.move_methods[square.piece.type](square)
                moves[square.piece] = piece_moves
        return moves

    def set_moves(self) -> None:
        """Sets all possible moves for all pieces, in the dictionary."""
        self.current_moves = self.get_moves()
        self.record_position()
    
    def set_piece_points(self) -> None:
        """Sets the number of points of material each player currently has."""
        self.piece_points = dict.fromkeys((Colour.WHITE, Colour.BLACK), 0)
        for square in self:
            if square.empty:
                continue
            points = PIECE_POINTS.get(square.piece.type, 0)
            self.piece_points[square.piece.colour] += points


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
