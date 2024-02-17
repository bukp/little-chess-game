This project in a simple chess programm to train at coding (and play during IT class). It handle :
 - a drag and drop GUI
 - all chess rules (castling, check, checkmate, pat, draw, ...)
 - a small chess bot (maybe 400 elo idk)
 - customisable pieces and board from lichess
 - possibility to play remotly with your friends very easily
 - possibility to go backward see your previous moves with mousewheel or directional arrows
 - import/export of PGN and FEN files formats

It contain:
 - An asset folder for pieces's sprites
 - A code folder containing two files :
    - chess.py which handle all chess things : boards, move, decision making, 
    - game.py which handle GUI
 - An executable file (equivalent to execute game.py)

To start a game :
 - execute chess.exe (or game.py)
 - In the settings window, press create to play the whites against the computer

I personnaly wrote the whole code of this project.
Sprites are taken from the open source chess site lichess.org.
The non-native libraries used in this project are pygame (GUI), cairo and Pillow (image converter).
