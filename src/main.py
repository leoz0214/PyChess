"""Main module of the program."""
import sys

import pygame as pg

from constants import WIDTH, HEIGHT, TITLE, FPS, SQUARE_WIDTH
from display import DisplayBoard


class Game:
    """The main class of the program, handling the chess game."""

    def __init__(self) -> None:
        self.window = pg.display.set_mode((WIDTH, HEIGHT))
        self.clock = pg.time.Clock()
        pg.display.set_caption(TITLE)
    
    def start(self) -> None:
        """Starts the game, including the main loop."""
        board = DisplayBoard(self.window, 100, SQUARE_WIDTH)
        while True:
            self.clock.tick(FPS)
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit(0)
            board.display()
            pg.display.update()


if __name__ == "__main__":
    pg.init()
    game = Game()
    game.start()
