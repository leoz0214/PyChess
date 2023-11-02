"""
Handles displaying the chess board and other game features
on the window of the program, not the actual internal data structures.
"""
from itertools import cycle

import pygame as pg

from board import Board, Square
from constants import (
    WIDTH, RANKS, FILES, DARK_SQUARE_COLOUR, LIGHT_SQUARE_COLOUR, PIECE_WIDTH,
    SELECTED_SQUARE_COLOUR, POSSIBLE_MOVE_CIRCLE_WIDTH,
    POSSIBLE_MOVE_CIRCLE_COLOUR, REVERSE_BOARD, TITLE)
from utils import Pieces


class DisplayBoard:
    """The chess board displayed on the screen. Centralised horizontally."""

    def __init__(
        self, window: pg.Surface, min_y: int, square_width: int
    ) -> None:
        self.window = window
        self.min_x = (WIDTH - square_width * FILES) // 2
        self.min_y = min_y
        self.max_x = self.min_x + square_width * FILES
        self.max_y = self.min_y + square_width * RANKS
        self.square_width = square_width
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
    
    def handle_click(self, coordinates: tuple[int, int]) -> None:
        """Handles a mouse click."""
        x, y = coordinates
        if not (
            self.min_x <= x <= self.max_x and self.min_y <= y <= self.max_y
        ):
            # Board not clicked.
            return
        file = (x - self.min_x) // self.square_width
        rank = FILES - 1 - (y - self.min_y) // self.square_width
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
        is_checkmate = self.board.is_checkmate
        if is_checkmate:
            print("Checkmate!")
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
            else self.colour)
        pg.draw.rect(self.board.window, colour, self)

        if not square.empty:
            coordinate = (
                self.left + (self.width - PIECE_WIDTH) // 2,
                self.top + (self.height - PIECE_WIDTH) // 2)
            self.board.window.blit(square.piece.image, coordinate)
        if any(square is move for move in self.board.possible_moves):
            pg.draw.circle(
                self.board.window, POSSIBLE_MOVE_CIRCLE_COLOUR,
                (self.centerx, self.centery), POSSIBLE_MOVE_CIRCLE_WIDTH)
