"""Main module of the program."""
import sys

import pygame as pg
pg.font.init()
pg.mixer.init()

import display
import home
from constants import *
from utils import render_text, Colour, Action


class Game:
    """The main class of the program, handling the chess game."""

    def __init__(self) -> None:
        self.window = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_icon(pg.image.load(ICON))
        self.clock = pg.time.Clock()
        # Persistent home screen - allow same settings to be
        # seen whenever returning to the home screen.
        self.home_display = home.Home(self)
    
    def home(self) -> None:
        """Displays the home screen."""
        pg.display.set_caption(TITLE)
        # Set started clicked to false.
        self.home_display.started = False
        while not self.home_display.started:
            self.clock.tick(FPS)
            events = pg.event.get()
            for event in events:
                match event.type:
                    case pg.QUIT:
                        pg.quit()
                        sys.exit(0)
                    case pg.MOUSEBUTTONDOWN:
                        if event.button in (1, 3):
                            coordinates = pg.mouse.get_pos()
                            self.home_display.handle_click(coordinates)
            self.home_display.display()
            pg.display.update()
        settings = self.home_display.settings
        while True:
            match self.start(settings):
                case Action.RESTART:
                    # Simply reload the game.
                    continue
                case Action.HOME:
                    # Exit current home function.
                    return
    
    def start(self, settings: "home.Settings") -> Action:
        """Starts the game, including the main loop."""
        pg.display.set_caption(TITLE)
        board = display.DisplayBoard(
            self, BOARD_MIN_X, BOARD_MIN_Y, SQUARE_WIDTH, settings)
        white_info = display.PlayerInfo(
            self, Colour.WHITE, WHITE_MIN_X, WHITE_MIN_Y,
            PLAYER_INFO_WIDTH, PLAYER_INFO_HEIGHT, PLAYER_INFO_FG)
        black_info = display.PlayerInfo(
            self, Colour.BLACK, BLACK_MIN_X, BLACK_MIN_Y,
            PLAYER_INFO_WIDTH, PLAYER_INFO_HEIGHT, PLAYER_INFO_FG)
        game_options = display.GameOptions(
            self, board, GAME_END_MIN_X, GAME_END_MIN_Y,
            GAME_END_WIDTH, GAME_END_HEIGHT)
        START_SFX.play()
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
                            game_options.handle_click(
                                coordinates, board.finished)
                            white_info.handle_click(coordinates, board)
                            black_info.handle_click(coordinates, board)
                            if game_options.restart:
                                # Exit current loop to replay the game.
                                return Action.RESTART
                            if game_options.home:
                                # Go back to the main menu.
                                return Action.HOME
                    case _:
                        if (
                            event.type == pg.MOUSEBUTTONUP
                            and event.button in (1, 3)
                            and board.confirm_deselect
                        ):
                            board.deselect()
                            continue
                        pressed = pg.mouse.get_pressed()
                        if (
                            (pressed[0] or pressed[2])
                            and board.selected_square is not None
                        ):
                            coordinates = pg.mouse.get_pos()
                            board.handle_drag(coordinates)
                        elif board.drag_coordinates is not None:
                            board.handle_drop()
            board.display()
            if not board.finished:
                board.register_time()
            white_info.display(board)
            black_info.display(board)
            game_options.display(board.finished)
            pg.display.update()

    def display_text(
        self, text: str, x: int, y: int, colour: str,
        size: int = 15, centre: bool = True
    ) -> None:
        """Displays text onto the window with no existing text object."""
        textbox = render_text(text, size, colour)
        self.display_rendered_text(textbox, x, y, centre)
    
    def display_rendered_text(
        self, textbox: pg.Surface, x: int, y: int, centre: bool = True,
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
    # Allows home screen to be accessed indefinitely.
    while True:
        game.home()
