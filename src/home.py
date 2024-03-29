"""
Module which handles the home screen of the game, where the players
can then proceed to start a game with particular settings.
"""
from dataclasses import dataclass

import pygame as pg

import main
from constants import *
from utils import render_text, surface_clicked


@dataclass
class Settings:
    """Bundles togeteher all the settings."""
    seconds: int | float
    added_seconds: int
    reverse: bool


class Home(pg.Rect):
    """Holds the home screen of the game."""

    def __init__(self, game: "main.Game") -> None:
        self.game = game
        # Width and height of the home rectangle simply
        # span the entire window.
        self.width = WIDTH
        self.height = HEIGHT
        self.fg = HOME_SCREEN_FG
        super().__init__(0, 0, self.width, self.height)

        self.title = render_text("Chess", 75, self.fg)
        self.title_coordinates = (self.centerx, 100)

        self.time_controls = TimeControlSetting(
            self.game, self, TIME_CONTROLS_MIN_X, TIME_CONTROLS_MIN_Y,
            TIME_CONTROLS_WIDTH, TIME_CONTROLS_HEIGHT,
            SELECTED_TIME_CONTROL_COLOUR)
        self.settings_box = SettingsBox(
            self.game, self, SETTINGS_MIN_X, SETTINGS_MIN_Y,
            SETTINGS_WIDTH, SETTINGS_HEIGHT)

        self.start = render_text("Start", 50, self.fg)
        self.start_coordinates = (self.centerx, 500)
        self.started = False
    
    def display(self) -> None:
        """Displays the home screen entirely."""
        pg.draw.rect(self.game.window, BACKGROUND_COLOUR, self)
        self.game.display_rendered_text(self.title, *self.title_coordinates)
        self.time_controls.display()
        self.settings_box.display()
        self.game.display_rendered_text(self.start, *self.start_coordinates)
    
    def handle_click(self, coordinates: tuple[int, int]) -> None:
        """Handles clicks for any of the settings."""
        self.time_controls.handle_click(coordinates)
        self.settings_box.handle_click(coordinates)
        if surface_clicked(self.start, *self.start_coordinates, coordinates):
            self.started = True
    
    @property
    def settings(self) -> Settings:
        """Returns the currently set settings."""
        seconds = self.time_controls.selected.seconds
        added_seconds = self.time_controls.selected.added_seconds
        reverse = self.settings_box.settings["reverse"].on
        return Settings(seconds, added_seconds, reverse)


class TimeControl(pg.Rect):
    """
    Represents a particular time control,
    with a fixed number of seconds and added seconds per move.
    """

    def __init__(
        self, game: "main.Game", seconds: int, added_seconds: int,
        display: str, min_x: int, min_y: int, width: int, height: int, fg: str
    ) -> None:
        self.game = game
        self.seconds = seconds
        self.added_seconds = added_seconds
        self.width = width
        self.height = height
        super().__init__(min_x, min_y, self.width, self.height)

        self.text = render_text(display, 20, fg)
        self.text_coordinates = (self.left + 10, self.top)
    
    def display(self, bg: str) -> None:
        """Displays the time control."""
        pg.draw.rect(self.game.window, bg, self, border_radius=10)
        self.game.display_rendered_text(
            self.text, *self.text_coordinates, centre=False)
    
    def clicked(self, coordinates: tuple[int, int]) -> None:
        """Check if particular coordinates clicked this time control."""
        return surface_clicked(
            self.text, *self.text_coordinates, coordinates, center=False)


class TimeControlSetting(pg.Rect):
    """Allows the players to select a time control, if any."""

    def __init__(
        self, game: "main.Game", home: Home, min_x: int, min_y: int,
        width: int, height: int, selected_colour: str
    ) -> None:
        self.game = game
        self.home = home
        self.width = width
        self.height = height
        self.selected_colour = selected_colour
        super().__init__(min_x, min_y, self.width, self.height)

        self.title = render_text("Time Control", 25, self.home.fg)
        self.title_coordinates = (self.left + 25, self.top + 25)

        self.time_controls = []
        for n, ((seconds, added_seconds), display) in enumerate(
            TIME_CONTROLS.items()
        ):
            row, column = divmod(n, TIME_CONTROLS_PER_ROW)
            top_left_coordinates = (
                self.left + 25 + column * TIME_CONTROL_WIDTH,
                self.top + 75 + row * TIME_CONTROL_HEIGHT)
            time_control = TimeControl(
                self.game, seconds, added_seconds, display,
                *top_left_coordinates, TIME_CONTROL_WIDTH, TIME_CONTROL_HEIGHT,
                self.home.fg)
            self.time_controls.append(time_control)
            
        self.selected = self.time_controls[0]
    
    def display(self) -> None:
        """Displays the available time controls."""
        self.game.display_rendered_text(
            self.title, *self.title_coordinates, centre=False)
        for time_control in self.time_controls:
            bg = (
                self.selected_colour if time_control is self.selected
                else BACKGROUND_COLOUR)
            time_control.display(bg)
    
    def handle_click(self, coordinates: tuple[int, int]) -> None:
        """
        Handles a click to see if any of the time control options were clicked.
        """
        for time_control in self.time_controls:
            if time_control.clicked(coordinates):
                self.selected = time_control
                return


class Setting(pg.Rect):
    """Represents and stores info for a single setting."""

    def __init__(
        self, game: "main.Game", display: str,
        min_x: int, min_y: int, width: int, height: int, fg: str,
        selected_colour: str, on: bool = False
    ) -> None:
        self.game = game
        self.width = width
        self.height = height
        self.selected_colour = selected_colour
        self.on = on
        super().__init__(min_x, min_y, self.width, self.height)

        self.text = render_text(display, 20, fg)
        self.text_coordinates = (self.left, self.top)
        self.on_text = render_text("ON", 20, fg)
        self.on_coordinates = (self.right - 80, self.top)
        self.off_text = render_text("OFF", 20, fg)
        self.off_coordinates = (self.right - 40, self.top)

    def display(self) -> None:
        """Displays the setting."""
        self.game.display_rendered_text(
            self.text, *self.text_coordinates, centre=False)
        if self.on:
            width, height = self.on_text.get_size()
            left, top = self.on_coordinates
        else:
            width, height = self.off_text.get_size()
            left, top = self.off_coordinates
        selected_rect = pg.rect.Rect(left, top, width, height)
        pg.draw.rect(
            self.game.window, SELECTED_SETTING_COLOUR,
            selected_rect, border_radius=10)
        self.game.display_rendered_text(
            self.on_text, *self.on_coordinates, centre=False)
        self.game.display_rendered_text(
            self.off_text, *self.off_coordinates, centre=False)
    
    def handle_click(self, coordinates: tuple[int, int]) -> None:
        """Checks if either ON/OFF has been clicked."""
        if surface_clicked(
            self.on_text, *self.on_coordinates, coordinates, center=False
        ):
            self.on = True
        elif surface_clicked(
            self.off_text, *self.off_coordinates, coordinates, center=False
        ):
            self.on = False


class SettingsBox(pg.Rect):
    """
    Allows players to adjust various other game settings other
    than the core one - time control. ON/OFF.
    """

    def __init__(
        self, game: "main.Game", home: Home, min_x: int, min_y: int,
        width: int, height: int
    ) -> None:
        self.game = game
        self.home = home
        self.width = width
        self.height = height
        super().__init__(min_x, min_y, self.width, self.height)

        self.title = render_text("Additional Settings", 25, self.home.fg)
        self.title_coordinates = (self.left + 25, self.top + 25)

        self.settings = {
            name: Setting(
                self.game, display, self.left + 25,
                self.top + 75 + n * SETTING_WIDTH, SETTING_WIDTH,
                SETTING_HEIGHT, self.home.fg, SELECTED_SETTING_COLOUR, on)
            for n, (name, (display, on)) in enumerate(SETTINGS.items())
        }

    def display(self) -> None:
        """Displays the settings."""
        self.game.display_rendered_text(
            self.title, *self.title_coordinates, centre=False)
        for setting in self.settings.values():
            setting.display()
    
    def handle_click(self, coordinates: tuple[int, int]) -> None:
        """Handles a coordinates click to see if any settings are changed."""
        for setting in self.settings.values():
            setting.handle_click(coordinates)
        