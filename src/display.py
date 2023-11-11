"""
Handles displaying the chess board and other game features
on the window of the program, not the actual internal data structures.
"""
from itertools import cycle

import pygame as pg

import main
from board import Board, Square
from constants import *
from pieces import Piece, Queen, Rook, Bishop, Knight
from utils import Colour, Pieces, render_text, surface_clicked, in_rectangle


class DisplayBoard:
    """The chess board displayed on the screen."""

    def __init__(
        self, game: "main.Game", min_x: int, min_y: int, square_width: int
    ) -> None:
        self.game = game
        self.window = self.game.window
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = self.min_x + square_width * FILES
        self.max_y = self.min_y + square_width * RANKS
        self.square_width = square_width
        self.width = self.square_width * FILES
        self.height = self.width
        self.board = Board()

        self.squares = []
        for rank in range(RANKS - 1, -1, -1):
            colour_cycle = cycle(
                (DARK_SQUARE_COLOUR, LIGHT_SQUARE_COLOUR) if rank % 2 == 0
                else (LIGHT_SQUARE_COLOUR, DARK_SQUARE_COLOUR))
            self.squares.append(
                [
                    DisplaySquare(self, colour, file, rank)
                    for colour, file in zip(colour_cycle, range(FILES))])
        
        self.selected_square = None
        self.result = None
        self.promotion = None
        self.checkmate_square = None
        self.stalemate_square = None
        self.possible_moves = []

    @property
    def in_reverse(self) -> bool:
        """Board display is inverted."""
        # White = 0, Black = 1.
        return REVERSE_BOARD and self.board.turn.value
    
    def display(self) -> None:
        """
        Displays all squares on the chess board.
        Reverse to face the side of black instead of white (if active).
        """
        for rank in self.squares:
            for square in rank:
                square.display(self.in_reverse)
        if self.result is not None:
            self.result.display()
        if self.promotion is not None:
            self.promotion.display()
    
    def handle_click(self, coordinates: tuple[int, int]) -> None:
        """Handles a mouse click."""
        if self.result is not None:
            self.result.to_close(coordinates)
            return
        if self.promotion is not None:
            if not self.promotion.closed:
                self.promotion.handle_click(coordinates)
            if self.promotion.closed:
                if self.promotion.selection is not None:
                    self.make_move(
                        self.promotion.square, self.promotion.selection)
                self.promotion = None
            return
        x, y = coordinates
        if not (
            self.min_x <= x <= self.max_x and self.min_y <= y <= self.max_y
        ):
            # Board not clicked.
            return
        file = (x - self.min_x) // self.square_width
        rank = RANKS - 1 - (y - self.min_y) // self.square_width
        if self.in_reverse:
            # File and rank are reversed (inverted board).
            file = FILES - 1 - file
            rank = RANKS - 1 - rank
        try:
            selected_square = self.board.get(file, rank)
        except IndexError:
            # Edge case - board not clicked after all.
            return
        if selected_square is self.selected_square:
            # Deselect the currently selected square and exit.
            self.selected_square = None
            self.possible_moves = []
            return
        if (
            (not selected_square.empty)
            and selected_square.piece.colour == self.board.turn
        ):
            self.selected_square = selected_square
            self.set_possible_moves()
        for move in self.possible_moves:
            if move is selected_square:
                self.make_move(move)
                break

    def set_possible_moves(self) -> None:
        """Sets the possible moves based on the selected square."""
        square = self.selected_square
        piece = square.piece
        self.possible_moves = self.board.current_moves[piece]
    
    def make_move(
        self, square: Square, promotion_piece: Piece | None = None
    ) -> None:
        """
        Makes a move with the currently selected piece.
        If coming from the promtion menu, the promotion piece is the
        piece to promote to.
        """
        is_en_passant = self.board.is_en_passant(
            self.selected_square, square)
        is_promotion = self.board.is_promotion(
            self.selected_square, square)
        is_castling = self.board.is_castling(
            self.selected_square, square, validate=False)
        from_before = self.selected_square.copy()
        to_before = square.copy()

        if is_en_passant:
            # Performs the special en passant capture.
            en_passant_victim = self.board.get(
                to_before.file, from_before.rank)
            en_passant_victim.piece = None

        if is_promotion:
            if promotion_piece is None:
                # Allows the player to choose the piece to promote the pawn to.
                self.promotion = PromotionMenu(
                    self, self.board.turn, square,
                    PROMOTION_WIDTH, PROMOTION_HEIGHT)
                return
            square.piece = promotion_piece
        else:
            square.piece = self.selected_square.piece

        if is_castling:
            kingside = square.file == 6
            rook_square = self.board.get(
                FILES - 1 if kingside else 0, square.rank)
            new_rook_square = self.board.get(5 if kingside else 3, square.rank)
            new_rook_square.piece = rook_square.piece
            rook_square.piece = None

        self.selected_square.piece = None
        from_after = self.selected_square.copy()
        to_after = square.copy()

        self.selected_square = None
        self.possible_moves.clear()

        self.board.add_move(
            from_before, to_before, from_after, to_after,
            is_en_passant, is_promotion, is_castling)
        self.checkmate_square = self.board.checkmate_square
        if self.checkmate_square is not None:
            title = (
                f"{TITLE} - {('White', 'Black')[self.board.turn.value]} wins")
            self.end(self.board.turn, title)
            return
        self.board.invert_turn()
        self.board.set_moves()
        if self.board.is_nfold_repetition(5):
            # Automatic draw upon 5 repetitions.
            self.end("Fivefold Repetition", f"{TITLE} - Fivefold Repetition")    
            return
        if self.board.is_nmove_rule(75):
            # 75 Move Rule automatic draw.
            self.end("75 Move Rule", f"{TITLE} - 75 Move Rule")
            return
        if self.board.is_insufficient_material:
            # Definitely not possible to checkmate. Game over.
            self.end(
                "Insufficient Material", f"{TITLE} - Insufficient Material")
            return
        if not any(moves for moves in self.board.current_moves.values()):
            # Not checkmate, but no legal moves i.e. stalemate.
            self.end("Stalemate", f"{TITLE} - Stalemate")
            for file in range(FILES):
                for rank in range(RANKS):
                    square = self.board.get(file, rank)
                    if (
                        (not square.empty) and square.piece.type == Pieces.KING
                        and square.piece.colour == self.board.turn
                    ):
                        self.stalemate_square = square
                        return
        pg.display.set_caption(
            f"{TITLE} - {('White', 'Black')[self.board.turn.value]} to play")

    def end(self, outcome: Colour | str, title: str) -> None:
        """Common function to handle game over (win/draw)."""
        self.finished = True
        self.result = DisplayResult(self, outcome, RESULT_WIDTH, RESULT_HEIGHT)
        pg.display.set_caption(title)


class DisplaySquare(pg.Rect):
    """Represents a square on the displayed chess board."""

    def __init__(
        self, board: DisplayBoard, colour: str, file: int, rank: int
    ) -> None:
        self.board = board
        self.colour = colour
        self.file = file
        self.rank = rank
        # Square: width = height.
        self.width = self.height = self.board.square_width
        self.normal_left = self.board.min_x + self.width * self.file
        # Remember, top rank is rank 7 internally.
        self.normal_top = (
            self.board.min_y + self.height * (RANKS - 1 - self.rank))
        # Swapped around display.
        self.reverse_left = (
            self.board.min_x + self.width * (FILES - 1 - self.file))
        self.reverse_top = (
            self.board.min_y + self.height * self.rank)
        super().__init__(
            self.normal_left, self.normal_top, self.width, self.height)

    def display(self, reverse: bool) -> None:
        """Displays the square."""
        if not reverse:
            self.left = self.normal_left
            self.top = self.normal_top
        else:
            self.left = self.reverse_left
            self.top = self.reverse_top

        square = self.board.board.get(self.file, self.rank)
        colour = (
            SELECTED_SQUARE_COLOUR if square is self.board.selected_square
            else RED if square is self.board.checkmate_square
            else GREY if square is self.board.stalemate_square
            else self.colour)
        pg.draw.rect(self.board.window, colour, self)

        if not square.empty:
            coordinate = (
                self.left + (self.width - PIECE_WIDTH) // 2,
                self.top + (self.height - PIECE_WIDTH) // 2)
            self.board.window.blit(square.piece.image, coordinate)
        if square in self.board.possible_moves:
            pg.draw.circle(
                self.board.window, POSSIBLE_MOVE_CIRCLE_COLOUR,
                (self.centerx, self.centery), POSSIBLE_MOVE_CIRCLE_WIDTH)


class DisplayResult(pg.Rect):
    """Displays the result of the game."""

    def __init__(
        self, board: DisplayBoard, outcome: Colour | str,
        width: int, height: int
    ) -> None:
        self.board = board
        self.width = width
        self.height = height
        self.left = self.board.min_x + (self.board.width - self.width) // 2
        self.top = self.board.min_y + (self.board.height - self.height) // 2
        outcome_text = "Checkmate" if isinstance(outcome, Colour) else outcome
        outcome_size = OUTCOME_TEXT_SIZES[outcome_text]
        self.outcome_textbox = render_text(outcome_text, outcome_size, GREY)
        info_text, colour = {
            Colour.WHITE: ("White wins!", WHITE),
            Colour.BLACK: ("Black wins!", BLACK),
        }.get(outcome, ("Draw", GREY))
        self.info_textbox = render_text(info_text, 30, colour)
        self.close_x = render_text("x", 30, GREY)
        self.close_x_coordinates = (self.left + self.width - 20, self.top + 20)
        self.closed = False
        super().__init__(self.left, self.top, self.width, self.height)

    def display(self) -> None:
        """Displays the outcome."""
        if self.closed:
            return
        pg.draw.rect(self.board.window, RESULT_COLOUR, self)
        self.board.game.display_rendered_text(
            self.outcome_textbox, self.centerx, self.top + 75)
        self.board.game.display_rendered_text(
            self.info_textbox, self.centerx, self.top + 150)
        self.board.game.display_rendered_text(
            self.close_x, *self.close_x_coordinates)
    
    def to_close(self, coordinates: tuple[int, int]) -> None:
        """Checks if the close button was clicked. If so, close the popup."""
        if (not self.closed) and surface_clicked(
            self.close_x, *self.close_x_coordinates, coordinates
        ):
            self.closed = True


class PromotionMenu(pg.Rect):
    """
    Allows the player to select a piece to promote a pawn to.
    The possible pieces are: Queen, Rook, Bishop and Knight.
    """

    def __init__(
        self, board: DisplayBoard, colour: Colour, move: Square,
        width: int, height: int
    ) -> None:
        self.board = board
        self.width = width
        self.height = height
        self.left = self.board.min_x + (self.board.width - self.width) // 2
        self.top = self.board.min_y + (self.board.height - self.height) // 2
        self.square = move
        super().__init__(self.left, self.top, self.width, self.height)
        # Pairs of pieces and their TOP LEFT CORNER co-ordinate.
        self.pieces = [
            (piece(colour), (
                self.centerx + PIECE_WIDTH * (i - 2), self.top + 50))
            for i, piece in enumerate((Queen, Rook, Bishop, Knight))]
        self.selection = None
        self.closed = False
        self.close_x = render_text("x", 30, GREY)
        self.close_x_coordinates = (self.left + self.width - 20, self.top + 20)
    
    def display(self) -> None:
        """Displays the promotion menu."""
        pg.draw.rect(self.board.window, PROMOTION_COLOUR, self)
        for piece, top_left in self.pieces:
            self.board.window.blit(piece.image, top_left)
        self.board.game.display_rendered_text(
            self.close_x, *self.close_x_coordinates)

    def handle_click(self, coordinates: tuple[int, int]) -> None:
        """Check for a piece click, or the X to cancel."""
        for piece, top_left in self.pieces:
            bottom_right = (
                top_left[0] + PIECE_WIDTH, top_left[1] + PIECE_WIDTH)
            if in_rectangle(coordinates, top_left, bottom_right):
                self.selection = piece
                self.closed = True
        if surface_clicked(
            self.close_x, *self.close_x_coordinates, coordinates
        ):
            self.closed = True
