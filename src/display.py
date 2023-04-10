"""
Handles displaying the chess board and other game features
on the window of the program, not the actual internal data structures.
"""
from itertools import cycle

import pygame as pg

from constants import (
    WIDTH, RANKS, FILES, DARK_SQUARE_COLOUR, LIGHT_SQUARE_COLOUR)


class DisplayBoard:
    """The chess board displayed on the screen. Centralised horizontally."""

    def __init__(
        self, window: pg.Surface, min_y: int, square_width: int
    ) -> None:
        self.window = window
        self.min_x = (WIDTH - square_width * FILES) // 2
        self.min_y = min_y
        self.square_width = square_width

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
        squares = self.squares if not reverse else reversed(self.squares)
        for rank in squares:
            for square in rank:
                square.display()  


class DisplaySquare(pg.Rect):
    """Represents a square on the displayed chess board."""

    def __init__(
        self, board: DisplayBoard, colour: str, file: int, rank: int
    ) -> None:
        self.board = board
        self.colour = colour
        # Square: width = height.
        width = height = self.board.square_width
        left = self.board.min_x + width * file
        # Remember, top rank is rank 7 internally.
        top = self.board.min_y + height * (RANKS - 1 - rank)
        super().__init__(left, top, width, height)

    def display(self) -> None:
        """Displays the square."""
        pg.draw.rect(self.board.window, self.colour, self)
