"""
Handles displaying the chess board and other game features
on the window of the program, not the actual internal data structures.
"""
from itertools import cycle

import pygame as pg

from board import Board, Square
from constants import (
    WIDTH, RANKS, FILES, DARK_SQUARE_COLOUR, LIGHT_SQUARE_COLOUR, PIECE_WIDTH,
    SELECTED_SQUARE_COLOUR)


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
    
    def display(self) -> None:
        """
        Displays all squares on the chess board.
        Reverse to face the side of black instead of white.
        """
        # White = 0, Black = 1.
        reverse = self.board.turn.value
        for rank in self.squares:
            for square in rank:
                square.display(reverse)
    
    def get_square(self, file: int, rank: int) -> Square:
        """Gets the internal square based on the file and rank."""
        return self.board.board[RANKS - 1 - rank][file]
    
    def handle_click(self, coordinates: tuple[int, int]) -> None:
        """Handles a mouse click."""
        x, y = coordinates
        if not (
            self.min_x <= x <= self.max_x and self.min_y <= y <= self.max_y
        ):
            # Board not clicked.
            return
        reverse = self.board.turn.value
        file = (x - self.min_x) // self.square_width
        rank = FILES - 1 - (y - self.min_y) // self.square_width
        if reverse:
            # File and rank are reversed (inverted board).
            file = FILES - 1 - file
            rank = RANKS - 1 - rank
        selected_square = self.get_square(file, rank)
        if selected_square == self.selected_square:
            # Deselect the currently selected square and exit.
            self.selected_square = None
            return
        if (
            selected_square.piece is not None
            and selected_square.piece.colour == self.board.turn
        ):
            self.selected_square = selected_square


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
        if (
            self.board.selected_square is not None
            and self.board.selected_square.file == self.file
            and self.board.selected_square.rank == self.rank
        ):
            # Square selected.
            colour = SELECTED_SQUARE_COLOUR
        else:
            colour = self.colour
        pg.draw.rect(self.board.window, colour, self)
        square = self.board.get_square(self.file, self.rank)
        if square.piece is not None:
            coordinate = (
                self.left + (self.width - PIECE_WIDTH) // 2,
                self.top + (self.height - PIECE_WIDTH) // 2)
            self.board.window.blit(square.piece.image, coordinate)
