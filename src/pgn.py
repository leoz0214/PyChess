"""
Module to allow the player to generate a PGN based on a
game played inside the app.
"""
import pathlib
import tkinter as tk
from dataclasses import dataclass
from tkinter import filedialog
from tkinter import messagebox

import pyglet

import display
from constants import *
from utils import OUTCOME_STRINGS


# Ensure Inter font works in Tkinter.
pyglet.font.add_file(str(FONT_DIR / "Inter.ttf"))


def inter(size: int, bold: bool = False, italic: bool = False) -> tuple:
    """Inter font utility function."""
    font = ("Inter", size)
    if bold:
        font += ("bold",)
    if italic:
        font += ("italic",)
    return font


def bool_to_state(boolean: bool) -> str:
    """True -> normal, False -> disabled"""
    return "normal" if boolean else "disabled"


@dataclass
class PGNField:
    """PGN field which user can input."""
    key: str
    display: str
    max_length: int
    fg: str = PGN_FG
    disabled: bool = False


PGN_FIELDS = (
    PGNField("file", "File Path:", 32768, disabled=True),
    PGNField("event", "Event Name:", 64),
    PGNField("site", "Site Name:", 64),
    PGNField("round", "Round:", 32),
    PGNField("white", "White Name:", 64, WHITE),
    PGNField("black", "Black Name:", 64, BLACK),
)


class PGNGenerator(tk.Tk):
    """Window for PGN generation."""

    def __init__(self, board: "display.DisplayBoard") -> None:
        super().__init__()
        self.title(f"{TITLE} - Save PGN")
        self.tk_setPalette(foreground=PGN_FG, background=BACKGROUND_COLOUR)
        self.resizable(False, False)
        self.iconbitmap(ICON)
        self.board = board
        self.confirmed_overwrite = False
        
        self.info_label = tk.Label(
            self, font=inter(15, italic=True),
            text="File path required, other fields optional.")
        self.info_label.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

        self.entries = {}
        for row, field in enumerate(PGN_FIELDS, 1):
            label = tk.Label(
                self, font=inter(15), text=field.display, fg=field.fg)
            entry = PGNEntry(
                self, field.max_length, fg=field.fg,
                state=bool_to_state(not field.disabled))
            label.grid(row=row, column=0, padx=5, pady=5, sticky="e")
            entry.grid(row=row, column=1, padx=5, pady=5)
            self.entries[field.key] = entry
        
        self.algebraic_notation_type = AlgebraicNotationTypeFrame(self)
        self.select_file_button = tk.Button(
            self, font=inter(20), text="Set File", width=15,
            command=self.set_file)
        self.save_button = tk.Button(
            self, font=inter(20), text="Save", width=15, command=self.save,
            state="disabled")
        
        self.algebraic_notation_type.grid(
            row=len(PGN_FIELDS) + 1, column=0, columnspan=2, padx=5, pady=5)
        self.select_file_button.grid(
            row=len(PGN_FIELDS) + 2, column=0, columnspan=2, padx=5, pady=5)
        self.save_button.grid(
            row=len(PGN_FIELDS) + 3, column=0, columnspan=2, padx=5, pady=5)
    
    def set_file(self) -> None:
        """Allows the player to select the file path to save to."""
        file = filedialog.asksaveasfilename(
            confirmoverwrite=True, defaultextension=".pgn",
            filetypes=(("PGN", ".pgn"),))
        if not file:
            return
        self.confirmed_overwrite = pathlib.Path(file).is_file()
        self.entries["file"].variable.set(file)
        self.update_state()

    def update_state(self) -> None:
        """Updates save button state based on if file has been set."""
        self.save_button.config(
            state=bool_to_state(self.entries["file"].value))
    
    def get_tag_pairs_string(self) -> str:
        """Returns the tag pairs string based on game info and user input."""
        tag_pairs = {}
        if (event := self.entries["event"].value):
            tag_pairs["Event"] = event
        if (site := self.entries["site"].value):
            tag_pairs["Site"] = site
        tag_pairs["Date"] = self.board.date_started.strftime("%Y.%m.%d")
        if (round_ := self.entries["round"].value):
            tag_pairs["Round"] = round_
        if (white := self.entries["white"].value):
            tag_pairs["White"] = white
        if (black := self.entries["black"].value):
            tag_pairs["Black"] = black
        tag_pairs["Result"] = OUTCOME_STRINGS[self.board.winner]
        return "\n".join(
            f'[{key}: "{value}"]' for key, value in tag_pairs.items())
        
    def get_algebraic_notation_string(self) -> str:
        """Returns the algebraic notation for the moves played."""
        moves = self.board.board.moves
        is_long = self.algebraic_notation_type.is_long
        attribute = f"{'long_' if is_long else ''}algebraic_notation"
        algebraic_notation_pairs = [
            [getattr(move, attribute) for move in moves[i:i+2]]
            for i in range(0, len(moves), 2)]
        return " ".join(
            f"{n}. {' '.join(pair)}"
            for n, pair in enumerate(algebraic_notation_pairs, 1))
    
    def save(self) -> None:
        """Saves the PGN."""
        try:
            tag_pairs_string = self.get_tag_pairs_string()
            algebraic_notation_string = self.get_algebraic_notation_string()
            outcome_string = OUTCOME_STRINGS[self.board.winner]
            final_string = (
                f"{tag_pairs_string}\n\n{algebraic_notation_string} "
                f"{outcome_string}")
            file = pathlib.Path(self.entries["file"].value)
            if file.is_file() and not self.confirmed_overwrite:
                if not messagebox.askyesnocancel(
                    "Confirm Overwrite",
                        "The selected file already exists "
                        "and will be overwritten.\nAre you sure "
                        "you would like to proceed?", icon="warning"
                ):
                    return
            file.write_text(final_string, encoding="utf8")
            self.destroy()
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"An error has occurred while trying to save the PGN: {e}")


class PGNEntry(tk.Entry):
    """A particular input box for a given PGN tag."""

    def __init__(
        self, master: PGNGenerator, max_length: int, **kwargs
    ) -> None:
        self.variable = tk.StringVar()
        self.variable.trace("w", lambda *_: self.validate())
        super().__init__(
            master, font=inter(15), width=32,
            textvariable=self.variable, disabledbackground=BACKGROUND_COLOUR,
            **kwargs)
        self.config(disabledforeground=self["fg"])
        self.max_length = max_length
        self.previous = ""
    
    def validate(self) -> None:
        """Validates the current input is valid (not too long)."""
        current = self.variable.get()
        if len(current) > self.max_length:
            self.variable.set(self.previous)
            return
        self.previous = current
    
    @property
    def value(self) -> str:
        return self.variable.get().strip()


class AlgebraicNotationTypeFrame(tk.Frame):
    """
    Allows players to choose either standard or long algebraic
    notation when saving the PGN.
    """

    def __init__(self, master: PGNGenerator) -> None:
        super().__init__(master)
        self.label = tk.Label(self, font=inter(15), text="Algebraic Notation:")
        self.label.pack(side="left")
        self.variable = tk.IntVar(value=0)
        for i, text in enumerate(("Standard", "Long")):
            radiobutton = tk.Radiobutton(
                self, font=inter(15), text=text, width=15,
                variable=self.variable, value=i)
            radiobutton.pack(side="left")
    
    @property
    def is_long(self) -> bool:
        return bool(self.variable.get())
