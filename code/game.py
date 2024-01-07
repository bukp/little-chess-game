import tkinter as tk
from tkinter import ttk
import os
import pygame
import random
import chess

dark_color, light_color = (181, 136, 99), (240, 217, 181)

def pos_to_coord(tup):
    """Convert pixels (mouse for example) coordinates into row/column coordinates"""
    if board_side == "white":
        return (7-int(tup[1]/(board_size//8)), int(tup[0]/(board_size//8)))
    elif board_side == "black" :
        return (int(tup[1]/(board_size//8)), 7-int(tup[0]/(board_size//8)))

def coord_to_pos(tup):
    """Convert row/column coordinates into pixels coordinates"""
    if board_side == "white":
        return ((board_size//8)*tup[1], (board_size//8)*7-(board_size//8)*tup[0])
    elif board_side == "black" :
        return ((board_size//8)*7-(board_size//8)*tup[1], (board_size//8)*tup[0])

def draw_board(board : chess.Board, held_piece : tuple, held_piece_moves : list, mouse_pos : tuple):
    """Draw the board"""
    for row in range(8):
        for col in range(8):
            color = dark_color
            if (row+col)%2 == 1 : # color white/black squares
                color = light_color
            if held_piece != None and held_piece == (row, col): 
                color = (color[0] - 75, color[1] - 50, color[2] + 30)
            if board.last_move != None and (row, col) in board.last_move: 
                color = (color[0] - 70, color[1] - 20, color[2] - 70)
            
            pygame.draw.rect(window_surface, color, pygame.Rect(*coord_to_pos((row, col)), board_size//8, board_size//8)) #Draw the square

            #Draw held piece effets 
            if (row, col) in held_piece_moves :
                color = (color[0] - 75, color[1] - 50, color[2] + 30)
                if pos_to_coord(mouse_pos) == (row, col):
                    pygame.draw.rect(window_surface, color, pygame.Rect(*coord_to_pos((row, col)), board_size//8, board_size//8)) # Draw a full rectangle under the piece if it can move there
                else :
                    if board[row, col] != None:  # Draw circles where the piece can go (full if the square is empty, else empty to allow the user to see the piece)
                        pygame.draw.circle(window_surface, color, (coord_to_pos((row, col))[0]+board_size//16, coord_to_pos((row, col))[1]+board_size//16), board_size//16, board_size//96)
                    else :
                        pygame.draw.circle(window_surface, color, (coord_to_pos((row, col))[0]+board_size//16, coord_to_pos((row, col))[1]+board_size//16), board_size//48)

            if (row, col) != held_piece and board[row, col] != None:  # Draw the piece unless it's held (sprites taken from lichess)
                window_surface.blit(sprites[board[row, col].letter.lower() if board[row, col].color == 1 else board[row, col].letter], coord_to_pos((row, col)))

    if held_piece != None: # If the piece is hels, draw it under the mouse
        window_surface.blit(sprites[board[held_piece].letter.lower() if board[held_piece].color == 1 else board[held_piece].letter], (mouse_pos[0] - board_size//16, mouse_pos[1] - board_size//16))

def promotion_choice(color, mouse_pos):
    """Draw promotion window"""
    pygame.draw.rect(window_surface, (255, 255, 255), pygame.Rect(0, 0, board_size//4, board_size//4))
    mouse_pos = (7-int(mouse_pos[1]/(board_size//8)), int(mouse_pos[0]/(board_size//8)))
    if mouse_pos[1] <= 1 and mouse_pos[0] >= 6 :
        pygame.draw.rect(window_surface, (175, 175, 175), pygame.Rect((board_size//8)*mouse_pos[1], ((board_size//8)*7)-(board_size//8)*mouse_pos[0], (board_size//8), (board_size//8)))
    d = {"Q" : (0, 0), "R" : ((board_size//8), 0), "B" : (0, (board_size//8)), "N" : ((board_size//8), (board_size//8))}
    for i in d:
        window_surface.blit(sprites[i.lower() if color == 1 else i], d[i])

def draw_popup(text):
    """Draw en game popup"""
    grey_surface = pygame.Surface((board_size, board_size))
    grey_surface.fill((50, 50, 50))
    grey_surface.set_alpha(125)
    window_surface.blit(grey_surface, (0, 0))
    cell_size = board_size//8
    pygame.draw.rect(window_surface, (255, 255, 255), pygame.Rect(cell_size*2, cell_size*3, cell_size*4, cell_size*2))
    pygame.draw.rect(window_surface, (0, 0, 0), pygame.Rect(cell_size*2, cell_size*3, cell_size*4, cell_size*2), max(1, int(3*board_size/480)))

    text1 = pygame.font.SysFont("FreeSans Gras", 300).render(text[0], True, (0, 0, 0), (255, 255, 255))
    coef = int(cell_size*8/10)/max(text1.get_height(), text1.get_width()//4)
    surf = pygame.Surface(text1.get_size())
    surf.blit(text1, (0, 0))
    text1 = pygame.transform.smoothscale(surf, (int(surf.get_width()*coef), int(surf.get_height()*coef)))

    text2 = pygame.font.SysFont("FreeSans Gras", 300).render(text[1], True, (0, 0, 0), (255, 255, 255))
    coef = int(cell_size*8/10)/max(text2.get_height(), text2.get_width()//4)
    surf = pygame.Surface(text2.get_size())
    surf.blit(text2, (0, 0))
    text2 = pygame.transform.smoothscale(surf, (int(surf.get_width()*coef), int(surf.get_height()*coef)))

    text = pygame.Surface((int(cell_size*4*9/10), int(cell_size*2*9/10)))
    text.fill((255, 255, 255))
    text.blit(text1, (text.get_width()/2 - text1.get_width()/2,text.get_height()/4 - text1.get_height()/2))
    text.blit(text2, (text.get_width()/2 - text2.get_width()/2,text.get_height()*3/4 - text2.get_height()/2))
    window_surface.blit(text, (board_size//2-text.get_width()/2, board_size//2-text.get_height()/2))

def start_a_game(settings = ("player", "bot"), bsd = "white", bsz = 480, board = "start", pieces_style = "cburnett"):
    global board_side
    global board_size
    board_side = bsd
    board_size = (bsz//8)*8

    #Load piece's sprites
    global sprites
    sprites = {i : None for i in ["K", "P", "N", "B", "R", "Q", "k", "p", "n", "b", "r", "q"]}
    for i in sprites:
        sprites[i] = pygame.image.load(f"asset/{pieces_style}/{('b' if i.islower() else 'w')+i.upper()}.png")
        sprites[i] = pygame.transform.smoothscale(sprites[i], (int(sprites[i].get_width() * (board_size//8)/max(sprites[i].get_size())), int(sprites[i].get_height() * (board_size//8)/max(sprites[i].get_size()))))

    #Initialise the window
    pygame.init()
    pygame.display.set_caption("Chess game")
    pygame.display.set_icon(sprites["N"])
    global window_surface
    window_surface = pygame.display.set_mode((board_size, board_size))

    running = True
    clock = pygame.time.Clock()
    mouse_pos = (0, 0)
    held_piece = None
    held_piece_moves = []

    board = chess.Board(board)

    while running :
        clock.tick(60)
        pygame.display.flip()
        draw_board(board, held_piece, held_piece_moves, mouse_pos)

        if board.get_state() != "Running" : #If game is over
            draw_board(board, held_piece, held_piece_moves, mouse_pos)
            draw_popup(board.get_state())
            pygame.display.flip()
            while running:
                clock.tick(60)
                for event in pygame.event.get(): #Wait for user to quit the window
                    if event.type == pygame.QUIT or event.type == pygame.MOUSEBUTTONDOWN:
                        running = False

        elif running :
            if settings[board.turn] == "player": #Check if it's the player turn
                for event in pygame.event.get():

                    if event.type == pygame.QUIT:
                        running = False

                    if board.get_state() == "Running" :

                        if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION]: #Get mouse pos
                            mouse_pos = event.pos

                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: #Get the left click and places the piece in the hand if there is one at the click location
                            pos = pos_to_coord(event.pos)
                            if board[pos] != None and board[pos].color == board.turn:
                                held_piece = pos
                                held_piece_moves = []
                                lis = board.get_moves_starting_with(held_piece)
                                for i in lis:
                                    if i[1] not in lis:
                                        held_piece_moves.append(i[1])

                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3: #Drop the piece if right click
                            held_piece = None
                            held_piece_moves = []

                        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                            moves, lis = board.get_moves_starting_with(held_piece), [] #Get all possible moves
                            for i in moves: #Get all moves ending at the click location
                                lis.append(i[1])

                            choices = []
                            if pos_to_coord(event.pos) in lis:
                                for i in moves:
                                    if (i[0], i[1]) == (held_piece, pos_to_coord(event.pos)):
                                        choices.append(i)

                                if len(choices) > 1:  #In case several moves end in the same square (promotion)
                                    move_to_play = None
                                    draw_board(board, None, [], mouse_pos)
                                    while move_to_play == None:
                                        clock.tick(60)
                                        promotion_choice(board.turn, mouse_pos)
                                        pygame.display.flip()

                                        for event in pygame.event.get():

                                            if event.type == pygame.QUIT:
                                                move_to_play = "Cancel"
                                                running = False

                                            if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION]:
                                                mouse_pos = event.pos

                                            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                                                move_to_play = "Cancel" #Cancel promotion

                                            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                                                mouse_coord = (7-int(event.pos[1]/(board_size//8)), int(event.pos[0]/(board_size//8)))
                                                if mouse_coord[1] <= 1 and mouse_coord[0] >= 6:
                                                    move_to_play = choices[mouse_coord[0]*2-mouse_coord[1]-11] #Transform click location in move index
                                                else :
                                                    move_to_play = "Cancel" #Cancel promotion
                                else :
                                    move_to_play = choices[0] #If there is only one move available, choose it
                                if move_to_play != "Cancel":
                                    board = board.move(move_to_play)
                            held_piece = None
                            held_piece_moves = []

            elif settings[board.turn] == "bot": #Check if it's the bot turn
                if board.get_state() == "Running":
                    draw_board(board, None, [], mouse_pos)
                    pygame.display.flip()
                    board = board.move(board.choose_best_move(1)) #Play the move
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False

            elif settings[board.turn] == "random": #Checks if the round is to be played randomly
                if board.get_state() == "Running":
                    board = board.move(random.choice(board.get_all_possible_moves())) #Play the move
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False

if __name__ == "__main__":

    #Creation of the tkinter setting window
    
    size = (600, 150)
    window = tk.Tk()
    window.title("Game settings")
    window.geometry(f"{size[0]}x{size[1]}")
    window.resizable(False, False)
    window.iconphoto(True, tk.PhotoImage(file = "asset/cburnett/wN.png"))
    window.columnconfigure(0, weight=1)
    window.rowconfigure(0, weight = 1)
    window.rowconfigure(1, weight = 1)
    window.rowconfigure(2, weight = 1)

    row1 = tk.Frame(window)
    row1.grid(row=0, column=0, sticky="ew")
    row1.columnconfigure(0, weight=1)
    row1.columnconfigure(1, weight=1)
    row1.columnconfigure(2, weight=1)
    row1.columnconfigure(3, weight=5)

    frame1 = tk.LabelFrame(row1, text = "White player")
    frame1.grid(row=0, column=0, sticky="nsew")

    frame2 = tk.LabelFrame(row1, text = "Black player")
    frame2.grid(row=0, column=1, sticky="nsew")

    frame3 = tk.LabelFrame(row1, text = "View")
    frame3.grid(row=0, column=2, sticky="nsew")

    frame4 = tk.Frame(row1)
    frame4.grid(row=0, column=3, sticky="nsew")

    frame5 = tk.Frame(window)
    frame5.grid(row=1, column=0, sticky="ew")
    frame5.columnconfigure(1, weight=1)

    frame6 = tk.LabelFrame(window, text = "Style")
    frame6.grid(row=2, column=0, sticky="nsew")
    frame6.columnconfigure(0, weight=1)
    frame6.columnconfigure(1, weight=2)
    frame6.columnconfigure(2, weight=1)
    frame6.columnconfigure(3, weight=2)

    liste1 = tk.Listbox(frame1, height = 3, selectmode = tk.SINGLE, exportselection = 0, activestyle = "none")
    liste1.pack()
    liste1.insert(1, "player")
    liste1.insert(2, "bot")
    liste1.insert(3, "random")
    liste1.select_set(0)

    liste2 = tk.Listbox(frame2, height = 3, selectmode = tk.SINGLE, exportselection = 0, activestyle = "none")
    liste2.pack()
    liste2.insert(1, "player")
    liste2.insert(2, "bot")
    liste2.insert(3, "random")
    liste2.select_set(1)

    liste3 = tk.Listbox(frame3, height = 2, selectmode = tk.SINGLE, exportselection = 0, activestyle = "none")
    liste3.pack()
    liste3.insert(1, "white")
    liste3.insert(2, "black")
    liste3.select_set(0)

    tk.Label(frame4, text = "Window size : ").pack()

    size_set = tk.StringVar()
    spinbox = tk.Spinbox(frame4, values = (120, 240, 360, 480, 600, 720, 840, 960), width = 5, textvariable = size_set)
    size_set.set("480")
    spinbox.pack(expand = tk.Y)

    def create():
        arg = ((liste1.get(liste1.curselection()[0]),liste2.get(liste2.curselection()[0])), liste3.get(liste3.curselection()[0]), int(size_set.get()), fen_entry.get(), pieces_style_list.get())
        print(pieces_style_list.get())
        window.destroy()
        start_a_game(*arg)

    tk.Button(frame4, text="Create", command = create).pack(fill=tk.X, expand=True)

    tk.Label(frame5, text = "Fen : ").grid(row=0, column=0, sticky="w")

    fen_entry = tk.Entry(frame5)
    fen_entry.grid(row=0, column=1, sticky="ew")
    fen_entry.insert(0, "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
    
    tk.Label(frame6, text = "Pieces : ").grid(row=0, column=0, sticky="w")

    pieces_style_list = ttk.Combobox(frame6, values=os.listdir("asset"), state="readonly")
    pieces_style_list.grid(row=0, column=1, sticky="ew")
    pieces_style_list.current(os.listdir("asset").index('cburnett'))

    tk.Label(frame6, text = "Board : ").grid(row=0, column=2, sticky="w")

    board_style_list = ttk.Combobox(frame6, state="readonly", values=["None"])
    board_style_list.grid(row=0, column=3, sticky="ew")
    board_style_list.current(0)

    window.mainloop()