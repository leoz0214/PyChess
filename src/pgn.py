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

import board
import display
from constants import *
from utils import Colour, Pieces, PIECE_LETTERS, FILE_STRING, OUTCOME_STRINGS


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


class PGNBoard(board.Board):
    """
    Subclass of Board to specialise in PGN file/rank disambiguation
    (minimise verbosity of algebraic notation source squares).
    Most board features will not be used apart from storing board
    state, a few convenient methods/getters etc.
    """

    def make_move(self, move: board.Move) -> None:
        """Makes an already checked, legal move (post-game)."""
        from_square = self.get(move.from_before.file, move.from_before.rank)
        from_square.piece = None
        to_square = self.get(move.to_before.file, move.to_before.rank)
        to_square.piece = move.to_after.piece
        if move.en_passant:
            rank = FILES - 3 - 1 if self.turn == Colour.WHITE else 3
            en_passant_square = self.get(to_square.file, rank)
            en_passant_square.piece = None
        if move.castling:
            kingside = to_square.file == FILES - 2
            if kingside:
                rook_square = self.get(FILES - 1, from_square.rank)
                rook_dest_square = self.get(FILES - 3, from_square.rank)
            else:
                rook_square = self.get(0, from_square.rank)
                rook_dest_square = self.get(4, from_square.rank)
            rook = rook_square.piece
            rook_square.piece = None
            rook_dest_square.piece = rook
        self.invert_turn()
        self.moves.append(move)

    def get_source_square_notation(
        self, src_file: int, src_rank: int, dest_file: int, dest_rank: int,
        is_capture: bool
    ) -> str:
        """
        Returns the most concise source square notation without ambiguity.
        - Ideally does not need to be explicitly stated.
        - File preferred next if required.
        - Rank preferred next if required.
        - File and rank last resort (full square).
        """
        src_square = self.get(src_file, src_rank)
        src_piece = src_square.piece
        dest_square = self.get(dest_file, dest_rank)
        file_ambiguity = False
        rank_ambiguity = False
        for square in self:
            if square is src_square or square.empty:
                continue
            piece = square.piece
            if piece.type != src_piece.type:
                continue
            possible_moves = self.move_methods[piece.type](square)
            if dest_square in possible_moves:
                if square.file != src_file:
                    file_ambiguity = True
                if square.rank != src_rank:
                    rank_ambiguity = True
                if file_ambiguity and rank_ambiguity:
                    return f"{FILE_STRING[src_file]}{src_rank + 1}"
        if file_ambiguity or (src_piece.type == Pieces.PAWN and is_capture):
            return FILE_STRING[src_file]
        if rank_ambiguity:
            return str(src_rank + 1)
        return ""


class PGNGenerator(tk.Tk):
    """Window for PGN generation."""

    def __init__(self, board: "display.DisplayBoard") -> None:
        super().__init__()
        self.title(f"{TITLE} - Save PGN")
        self.tk_setPalette(foreground=PGN_FG, background=BACKGROUND_COLOUR)
        self.resizable(False, False)
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
        event = self.entries["event"].value
        if event:
            tag_pairs["Event"] = event
        site = self.entries["site"].value
        if site:
            tag_pairs["Site"] = site
        tag_pairs["Date"] = self.board.date_started.strftime("%Y.%m.%d")
        round_ = self.entries["round"].value
        if round_:
            tag_pairs["Round"] = round_
        white = self.entries["white"].value
        if white:
            tag_pairs["White"] = white
        black = self.entries["black"].value
        if black:
            tag_pairs["Black"] = black
        tag_pairs["Result"] = OUTCOME_STRINGS[self.board.winner]
        return "\n".join(
            f'[{key}: "{value}"]' for key, value in tag_pairs.items())
        
    def get_algebraic_notation_string(self) -> str:
        """Returns the algebraic notation for the moves played."""
        moves = self.board.board.moves
        algebraic_notation_pairs = []
        pgn_board = PGNBoard()
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
                    dest_square = move.to_before
                    is_capture = not dest_square.empty or move.en_passant

                    src_string = pgn_board.get_source_square_notation(
                        src_square.file, src_square.rank,
                        dest_square.file, dest_square.rank, is_capture)
                    
                    dest_file = FILE_STRING[dest_square.file]
                    dest_rank = dest_square.rank + 1

                    capture_char = "x" if is_capture else ""

                    if move.promotion:
                        promotion_piece_letter = PIECE_LETTERS.get(
                            move.to_after.piece.type)
                        promotion_string = f"={promotion_piece_letter}"
                    else:
                        promotion_string = ""
                    algebraic_notation = (
                        f"{piece_letter}{src_string}{capture_char}"
                        f"{dest_file}{dest_rank}{promotion_string}")
                if move.check:
                    algebraic_notation += "+"
                if move.checkmate:
                    algebraic_notation += "#"
                pair.append(algebraic_notation)
                pgn_board.make_move(move)
            algebraic_notation_pairs.append(pair)
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
