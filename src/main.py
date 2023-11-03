"""Main module of the program."""
import sys

import pygame as pg

import display
from constants import (
    WIDTH, HEIGHT, TITLE, FPS, SQUARE_WIDTH, BACKGROUND_COLOUR,
    BOARD_MIN_X, BOARD_MIN_Y)
from utils import render_text


pg.font.init()


class Game:
    """The main class of the program, handling the chess game."""

    def __init__(self) -> None:
        self.window = pg.display.set_mode((WIDTH, HEIGHT))
        self.clock = pg.time.Clock()
        pg.display.set_caption(TITLE)
    
    def start(self) -> None:
        """Starts the game, including the main loop."""
        board = display.DisplayBoard(
            self, BOARD_MIN_X, BOARD_MIN_Y, SQUARE_WIDTH)
        while True:
            self.clock.tick(FPS)
            self.window.fill(BACKGROUND_COLOUR)
            events = pg.event.get()
            for event in events:
                match event.type:
                    case pg.QUIT:
                        pg.quit()
                        sys.exit(0)
                    case pg.MOUSEBUTTONDOWN:
                        # Accept left click (1) or right click (3).
                        if event.button in (1, 3):
                            coordinates = pg.mouse.get_pos()
                            board.handle_click(coordinates)
            board.display()
            pg.display.update()

    def display_text(
        self, text: str, x: int, y: int, colour: str,
        size: int = 15, centre: bool = True
    ) -> None:
        """Displays text onto the window with no existing text object."""
        textbox = render_text(text, size, colour)
        self.display_rendered_text(textbox, x, y, centre)
    
    def display_rendered_text(
        self, textbox: pg.Surface, x: int, y: int, centre: bool = True
    ) -> None:
        """
        Displays a text surface.
        If centre is True, the x and y co-ordinates are the centre,
        else x and y are taken to be the left and top respectively.
        """
        if not centre:
            left = x
            top = y
        else:
            left = x - textbox.get_width() // 2
            top = y - textbox.get_height() // 2
        self.window.blit(textbox, (left, top))


if __name__ == "__main__":
    pg.init()
    game = Game()
    game.start()
