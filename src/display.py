"""
Handles displaying the chess board and other game features
on the window of the program, not the actual internal data structures.
"""
from itertools import cycle

import pygame as pg

from board import Board, Square
from constants import (
    WIDTH, RANKS, FILES, DARK_SQUARE_COLOUR, LIGHT_SQUARE_COLOUR, PIECE_WIDTH)


class DisplayBoard:
    """The chess board displayed on the screen. Centralised horizontally."""

    def __init__(
        self, window: pg.Surface, min_y: int, square_width: int
    ) -> None:
        self.window = window
        self.min_x = (WIDTH - square_width * FILES) // 2
        self.min_y = min_y
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
    
    def display(self, reverse: bool = False) -> None:
        """
        Displays all squares on the chess board.
        Reverse to face the side of black instead of white.
        """
        for rank in self.squares:
            for square in rank:
                square.display(reverse)
    
    def get_square(self, file: int, rank: int) -> Square:
        """Gets the internal square based on the file and rank."""
        return self.board.board[RANKS - 1 - rank][file]


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
        pg.draw.rect(self.board.window, self.colour, self)
        square = self.board.get_square(self.file, self.rank)
        if square.piece is not None:
            coordinate = (
                self.left + (self.width - PIECE_WIDTH) // 2,
                self.top + (self.height - PIECE_WIDTH) // 2)
            self.board.window.blit(square.piece.image, coordinate)
