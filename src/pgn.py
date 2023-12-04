"""
Module to allow the player to generate a PGN based on a
game played inside the app.
"""
import tkinter as tk
from dataclasses import dataclass
from tkinter import filedialog
from tkinter import messagebox

import pyglet

import display
from constants import *
from utils import Colour, PIECE_LETTERS, FILE_STRING


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
    PGNField("event", "Event Name:", 64),
    PGNField("white", "White Name:", 64, WHITE),
    PGNField("black", "Black Name:", 64, BLACK),
    PGNField("file", "File Path:", 32768, disabled=True)
)


class PGNGenerator(tk.Tk):
    """Window for PGN generation."""

    def __init__(self, board: "display.DisplayBoard") -> None:
        super().__init__()
        self.title(f"{TITLE} - Save PGN")
        self.tk_setPalette(foreground=PGN_FG, background=BACKGROUND_COLOUR)
        self.resizable(False, False)
        self.board = board
        
        self.info_label = tk.Label(
            self, font=inter(15, italic=True),
            text="All names optional, but must specify a file path.")
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
        
        self.select_file_button = tk.Button(
            self, font=inter(20), text="Set File", width=15,
            command=self.set_file)
        self.save_button = tk.Button(
            self, font=inter(20), text="Save", width=15, command=self.save,
            state="disabled")
        
        self.select_file_button.grid(
            row=len(PGN_FIELDS) + 1, column=0, columnspan=2, padx=5, pady=5)
        self.save_button.grid(
            row=len(PGN_FIELDS) + 2, column=0, columnspan=2, padx=5, pady=5)
    
    def set_file(self) -> None:
        """Allows the player to select the file path to save to."""
        file = filedialog.asksaveasfilename(
            confirmoverwrite=True, defaultextension=".pgn",
            filetypes=(("PGN", ".pgn"),))
        if not file:
            return
        self.entries["file"].variable.set(file)
        self.update_state()

    def update_state(self) -> None:
        """Updates save button state based on if file has been set."""
        self.save_button.config(
            state=bool_to_state(self.entries["file"].value))
    
    def save(self) -> None:
        """Saves the PGN."""
        moves = self.board.board.moves
        algebraic_notation_pairs = []
        for i in range(0, len(moves), 2):
            pair = []
            for move in moves[i:i+2]:
                if move.castling:
                    kingside = move.to_before.file == 6
                    algebraic_notation = "O-O" if kingside else "O-O-O"
                else:
                    piece_letter = PIECE_LETTERS.get(
                        move.from_before.piece.type, "")

                    src_square = move.from_before
                    src_file = FILE_STRING[src_square.file]
                    src_rank = src_square.rank + 1
                    
                    dest_square = move.to_before
                    dest_file = FILE_STRING[dest_square.file]
                    dest_rank = dest_square.rank + 1

                    capture_char = "x" if (
                        not dest_square.empty or move.en_passant) else ""

                    if move.promotion:
                        promotion_piece_letter = PIECE_LETTERS.get(
                            move.to_after.piece.type)
                        promotion_string = f"={promotion_piece_letter}"
                    else:
                        promotion_string = ""
                    algebraic_notation = (
                        f"{piece_letter}{src_file}{src_rank}{capture_char}"
                        f"{dest_file}{dest_rank}{promotion_string}")
                if move.check:
                    algebraic_notation += "+"
                if move.checkmate:
                    algebraic_notation += "#"
                pair.append(algebraic_notation)
            algebraic_notation_pairs.append(pair)
        algebraic_notation_string = " ".join(
            f"{n}. {' '.join(pair)}"
            for n, pair in enumerate(algebraic_notation_pairs, 1))
        print(algebraic_notation_string)
        outcome_string = {
            Colour.WHITE: "1-0",
            Colour.BLACK: "0-1",
            None: "1/2-1/2"
        }[self.board.winner]
        print(outcome_string)


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
