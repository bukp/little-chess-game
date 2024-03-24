This project is a simple chess program designed to train coding skills (and play during IT class). It handles:
 - A drag-and-drop GUI
 - All chess rules (castling, check, checkmate, stalemate, draw, etc.)
 - A small chess bot (approximately 400 Elo, though this is an estimate)
 - Customizable pieces and boards from Lichess
 - The ability to play remotely with friends very easily
 - The ability to go backward and review previous moves using the mouse wheel or directional arrows
 - Import/export of PGN and FEN file formats

It contains:
 - An asset folder for piece sprites
 - A code folder containing two files:
    - chess.py, which handles all chess-related tasks (boards, moves, decision-making, etc.)
    - game.py, which handles the GUI
 - An executable file (equivalent to executing game.py)

To start a game:
 - Execute chess.exe (or game.py).
 - In the settings window, press "Create Board" to play as White against the computer.
 - To play a game over LAN, press "Create LAN Game" instead of "Create Board" and join the game with another computer on the same LAN.
 - Alternatively, enter IP addresses manually to connect with others.

I personally wrote the entire code for this project. Sprites are taken from the open-source chess site Lichess.org. The only libraries used in this project are Pygame (GUI), Cairo and Pillow (image converters).