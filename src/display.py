"""
Handles displaying the chess board and other game features
on the window of the program, not the actual internal data structures.
"""
from itertools import cycle

import pygame as pg

import main
from board import Board, Square
from constants import *
from utils import Colour, render_text, surface_clicked


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
        self.checkmate_square = None
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
    
    def handle_click(self, coordinates: tuple[int, int]) -> None:
        """Handles a mouse click."""
        if self.result is not None:
            self.result.to_close(coordinates)
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
            self.possible_moves.clear()
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
        self.possible_moves = self.board.move_methods[piece.type](square)
    
    def make_move(self, square: Square) -> None:
        """Makes a move with the currently selected piece."""
        from_before = self.selected_square.copy()
        to_before = square.copy()

        square.piece = self.selected_square.piece
        self.selected_square.piece = None

        from_after = self.selected_square.copy()
        to_after = square.copy()

        self.selected_square = None
        self.possible_moves.clear()

        self.board.add_move(from_before, to_before, from_after, to_after)
        self.checkmate_square = self.board.checkmate_square
        if self.checkmate_square is not None:
            self.finished = True
            self.result = DisplayResult(
                self, self.board.turn, RESULT_WIDTH, RESULT_HEIGHT)
            pg.display.set_caption(
                f"{TITLE} - {('White', 'Black')[self.board.turn.value]} wins")
            return
        self.board.invert_turn()
        pg.display.set_caption(
            f"{TITLE} - {('White', 'Black')[self.board.turn.value]} to play")


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
            else RED if square is self.board.checkmate_square else self.colour)
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
        self, board: DisplayBoard, winner: Colour | None,
        width: int, height: int
    ) -> None:
        self.board = board
        self.width = width
        self.height = height
        self.left = self.board.min_x + (self.board.width - self.width) // 2
        self.top = self.board.min_y + (self.board.height - self.height) // 2
        outcome_text = "Checkmate" if winner is not None else "Stalemate"
        self.outcome_textbox = render_text(outcome_text, 50, GREY)
        info_text, colour = {
            Colour.WHITE: ("White wins!", WHITE),
            Colour.BLACK: ("Black wins!", BLACK),
            None: ("Draw!", GREY)
        }[winner]
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
