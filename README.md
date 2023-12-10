# PyChess

PyChess is a Python/pygame implementation of the renowned game of Chess, a strategic board game that was invented over a millennium ago.

For now, in a nutshell, this implementation allows a match between two players, where the players share the same computer and make moves accordingly.

Of course, chess rules are fully supported, including handling special moves like en passant, castling and promotion, and detecting draw scenarios.

## Installation and Compatibility

There are two methods of running the app:
- Windows EXE
- Through Python itself

### Windows EXE

The app has been successfully converted to a **single** Windows executable file and can hence be run directly through the EXE.

All the separate resources such as audio and images have already been included in the EXE, so no additional files are required.

The executable can be found as part of the app release.

- Of course, this is only supported for **Windows**.
- The app may take some time to start up (10-15 seconds). Be patient, if that is the case.

### Python

The app is written in Python, so of course it can be executed directly through Python.

This section assumes working knowledge of Python setup. For further guidance, see the official Python website and related websites.

- The minimum supported Python version is **3.10**. The code has been written in 3.10, so definitely works in this version, and should continue to work in 3.11 and above.
- The app has only been developed on and tested on Windows. It may still work correctly on other operating systems, but this cannot be guaranteed.
- Along with Python installed, two third party libraries that the app depends on are: `pygame` and `pyglet`.
Install these using pip if required.

Provided the above conditions are met, follow these steps to complete setup:
1. Place the `audio`, `font`, `images` and `src` folder as seen in the project codebase into one folder, and also add the pychess.py script to the same folder. **All files and folders are required; the code will not run without them**.
2. Run the pychess.py script. This will start up the app.

---

Hopefully, regardless of setup method, you have successfully been able to start up the game.

## Features

Note, it is of course expected that you understand the basic chess rules before reading this section. If not, consider researching the rules first, otherwise much of this will make little sense.

Anyways, provided you are familiar with Chess, here are some of the features this implementation of the game includes.

### Starting a game

When the app is launched, you will see a starting screen where you can adjust the following:

- **Time control** - how much time does each player start with, and how much time is added per move? Examples include: 3 minutes (Blitz), 10 minutes (Rapid), and 1 | 1 (starting with 1 minute, 1 second added per move). By default, there is no time limit.
- **Automatically flip board** - whether or not to flip the board when it is Black's turn.

Once ready, click Start and the game will begin immediately.

### During the game

There are various features which ensure a smooth experience whilst playing:

- All pieces move correctly as per standard chess rules:
    - Pawns can move one square forward or diagonally (capture only). They can only move two squares on the first move, and can perform **en passant** and **promotion**. En passant legality is checked carefully.
    - Knights can move in a L-shape (2 squares in one direction and 1 square in the perpendicular direction).
    - Bishops can move diagonally.
    - Rooks can move horizontally and vertically.
    - Queens can move horizontally, vertically and diagonally.
    - Kings can only move to a surrounding safe square, and can also perform **castling** with either rook. Castling legality is checked carefully.
- Various standardised chess rules are handled:
    - **Checkmate** is registered once the opponent's King cannot escape capture.
    - **Stalemate** is registered if it's a players turn but they have no legal moves (draw).
    - **Fivefold repetition** is registered if the exact same position is reached 5 times (draw).
    - The **75 move rule** is registered if no pawn moves or captures have been made in the last 75 moves for both players (draw).
    - **Insufficient material** is detected if it is theoretically impossible for both players to checkmate the other player (draw).
    - If a player **times out**, the opponent usually wins. However, if the current player times out but the opponent has insufficient material, the game ends in a **timeout vs insufficient material** draw.
- Pieces can be **clicked** or **dragged and dropped** to move.
- A player can **resign**, rendering the opponent the winner.
- Optional draws are also possible:
    - **Mutual** - both players agree to a draw.
    - **Threefold repetition** - a player can claim a draw if the same position is reached 3 times.
    - **50 move rule** - a player can also claim a draw if no pawn moves or captures have been made in the last 50 moves for both players.
- Some **sound effects** enliven the experience. These sound effects are from chess.com. See the disclaimer regarding why this is acceptable usage of these sound effects.
- **Captured opponent pieces** are displayed for each player, and any points advantage is displayed for the appropriate player. The points value of pieces are: Pawn (1), Knight (3), Bishop (3), Rook (5), Queen (9).

### After the game

Here are some points to note regarding the post-game features of the app:

- The outcome is displayed, including how the game ended (Checkmate, Stalemate, Timeout etc.) and the winner (White, Black or Draw).
- It is then possible to **replay** (start a new game).
- A fancier feature is the ability to save a **PGN** file of the game, so whilst the app itself cannot perform analysis for example, the game can be exported to PGN, which can then be imported into other chess analysis sites/software.
    - PGN is a standardised chess file storing game information and the moves in algebraic notation.
    - PGN tags include:
        - Event name
        - Site name
        - Round
        - Date started (automatically included)
        - White name
        - Black name
        - Outcome (automatically included)
    The 5 non-automatically included fields can optionally be set or left blank.
    - The app requires a file path to export the PGN file to.
    - Either standard or long algebraic notation can be generated. Standard notation involves representing all moves as concisely as possible whereas long algebraic notation maximises explitness by always specifying the source square as required.

## Disclaimer

The project includes sound effects from chess.com. Despite this, as the project is just for fun, with **no plans whatsoever to spread the software**, this can be considered fair/trivial use.