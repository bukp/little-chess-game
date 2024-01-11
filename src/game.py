import tkinter as tk
from tkinter import ttk
import threading
import os
import pygame
import random
import chess

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

class DisplayBoard():
    def __init__(self, board, board_side, board_size, settings, sprites, pos = (0, 0)):
        self.board_side = board_side
        self.board_size = board_size
        self.settings = settings
        self.sprites = sprites
        self.pos = pos

        self.mouse = (0, 0)
        self.board = board
        self.move_to_play = None
        self.page = "current"
        self.sub_state = None
        self.temp_var = {}

    def draw_board(self, mouse_pos : tuple):
        """Draw the board"""
        board_surface = pygame.Surface((board_size, board_size))
        held_piece = self.temp_var["held_piece"] if "held_piece" in self.temp_var else None
        held_piece_moves = self.temp_var["held_piece_moves"] if "held_piece_moves" in self.temp_var else []
        board_surface.blit(self.sprites["Board"], (0, 0))
        for row in range(8):
            for col in range(8):
                #Draw held piece effets 
                if (row, col) in held_piece_moves or (row, col) == held_piece:
                    cell_surface = pygame.Surface((board_size//8, board_size//8), pygame.SRCALPHA)
                    color = (0, 100, 255, 100)
                    if held_piece == (row, col):
                        color = color[:3]+(50,)
                        cell_surface.fill(color)
                    elif pos_to_coord(mouse_pos) == (row, col) or held_piece == (row, col):
                        cell_surface.fill(color)
                    else :
                        if self.board[row, col] != None:  # Draw circles where the piece can go (full if the square is empty, else empty to allow the user to see the piece)
                            pygame.draw.circle(cell_surface, color, (board_size//16, board_size//16), board_size//16, board_size//96)
                        else :
                            pygame.draw.circle(cell_surface, color, (board_size//16, board_size//16), board_size//48)
                    board_surface.blit(cell_surface, coord_to_pos((row, col)))
                
                elif self.board.last_move != None and (row, col) in self.board.last_move:
                    color = (0, 180, 0, 75)
                    cell_surface = pygame.Surface((board_size//8, board_size//8), pygame.SRCALPHA)
                    cell_surface.fill(color)
                    board_surface.blit(cell_surface, coord_to_pos((row, col)))

                if (row, col) != held_piece and self.board[row, col] != None:  # Draw the piece unless it's held (sprites taken from lichess)
                    board_surface.blit(self.sprites[self.board[row, col].letter.lower() if self.board[row, col].color == 1 else self.board[row, col].letter], coord_to_pos((row, col)))

        if held_piece != None: # If the piece is hels, draw it under the mouse
            board_surface.blit(self.sprites[self.board[held_piece].letter.lower() if self.board[held_piece].color == 1 else self.board[held_piece].letter], (mouse_pos[0] - board_size//16, mouse_pos[1] - board_size//16))
        return board_surface

    def promotion_choice(self, surface, mouse_pos):
        """Draw promotion window"""
        pygame.draw.rect(surface, (255, 255, 255), pygame.Rect(0, 0, board_size//4, board_size//4))
        mouse_pos = (7-int(mouse_pos[1]/(board_size//8)), int(mouse_pos[0]/(board_size//8)))
        if mouse_pos[1] <= 1 and mouse_pos[0] >= 6 :
            pygame.draw.rect(surface, (175, 175, 175), pygame.Rect((board_size//8)*mouse_pos[1], ((board_size//8)*7)-(board_size//8)*mouse_pos[0], (board_size//8), (board_size//8)))
        d = {"Q" : (0, 0), "R" : ((board_size//8), 0), "B" : (0, (board_size//8)), "N" : ((board_size//8), (board_size//8))}
        for i in d:
            surface.blit(self.sprites[i.lower() if self.board.turn == 1 else i], d[i])
        return surface

    def draw_pop_up(self, text, surface):
        """Draw end game popup"""
        grey_surface = pygame.Surface((board_size, board_size))
        grey_surface.fill((50, 50, 50))
        grey_surface.set_alpha(125)
        surface.blit(grey_surface, (0, 0))
        cell_size = board_size//8
        pygame.draw.rect(surface, (255, 255, 255), pygame.Rect(cell_size*2, cell_size*3, cell_size*4, cell_size*2))
        pygame.draw.rect(surface, (0, 0, 0), pygame.Rect(cell_size*2, cell_size*3, cell_size*4, cell_size*2), max(1, int(3*board_size/480)))

        text1 = pygame.font.SysFont("FreeSans Gras", 300).render(text[0], True, (0, 0, 0), (255, 255, 255))
        coef = int(cell_size*9/10)/max(text1.get_height(), text1.get_width()//4)
        surf = pygame.Surface(text1.get_size())
        surf.blit(text1, (0, 0))
        text1 = pygame.transform.smoothscale(surf, (int(surf.get_width()*coef), int(surf.get_height()*coef)))

        text2 = pygame.font.SysFont("FreeSans Gras", 300).render(text[1], True, (0, 0, 0), (255, 255, 255))
        coef = int(cell_size*7/10)/max(text2.get_height(), text2.get_width()//4)
        surf = pygame.Surface(text2.get_size())
        surf.blit(text2, (0, 0))
        text2 = pygame.transform.smoothscale(surf, (int(surf.get_width()*coef), int(surf.get_height()*coef)))

        text = pygame.Surface((int(cell_size*4*9/10), int(cell_size*2*9/10)))
        text.fill((255, 255, 255))
        text.blit(text1, (text.get_width()/2 - text1.get_width()/2,text.get_height()/4 - text1.get_height()/2))
        text.blit(text2, (text.get_width()/2 - text2.get_width()/2,text.get_height()*3/4 - text2.get_height()/2))
        surface.blit(text, (board_size//2-text.get_width()/2, board_size//2-text.get_height()/2))
        return surface

    def handle_events(self, events):

        for event in events:

            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION): #Get mouse pos
                pointer = event.pos
                if self.pos[0] <= pointer[0] < self.pos[0] + self.board_size and self.pos[1] <= pointer[1] < self.pos[1] + self.board_size:
                    self.mouse = (pointer[0]-self.pos[0], pointer[1]-self.pos[1])
                else :
                    event = pygame.event.Event(pygame.MOUSEBUTTONUP, button = 1)
                    self.mouse = (-10, -10)

            if self.page == "current":
                if self.board.get_state() == "Running" :
                    if self.settings[self.board.turn] == "player": #Check if it's the player turn
                        if self.sub_state == None:
                            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: #Get the left click and places the piece in the hand if there is one at the click location
                                pos = pos_to_coord(self.mouse)
                                if self.board[pos] != None and self.board[pos].color == self.board.turn:
                                    self.temp_var["held_piece"] = pos
                                    self.temp_var["held_piece_moves"] = []
                                    lis = self.board.get_moves_starting_with(self.temp_var["held_piece"])
                                    for i in lis:
                                        self.temp_var["held_piece_moves"].append(i[1])

                            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3: #Drop the piece if right click
                                del self.temp_var["held_piece"]
                                del self.temp_var["held_piece_moves"]

                            if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and "held_piece" in self.temp_var:
                                moves, lis = self.board.get_moves_starting_with(self.temp_var["held_piece"]), [] #Get all possible moves
                                for i in moves: #Get all moves ending at the click location
                                    lis.append(i[1])

                                choices = []
                                if pos_to_coord(self.mouse) in lis:
                                    for i in moves:
                                        if (i[0], i[1]) == (self.temp_var["held_piece"], pos_to_coord(self.mouse)):
                                            choices.append(i)
                                if choices:
                                    if len(choices) == 1:
                                        self.move_to_play = choices[0]
                                        self.temp_var["held_piece"] = None
                                        self.temp_var["held_piece_moves"] = []
                                
                                    elif len(choices) > 1: #In case several moves end in the same square (promotion)
                                        self.sub_state = "promotion"
                                        self.temp_var = {}
                                        self.temp_var["choices"] = choices
                                else :
                                    self.temp_var = {}

                        elif self.sub_state == "promotion" :
                            
                            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                                self.move_to_play = "Cancel" #Cancel promotion

                            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                                mouse_coord = (7-int(self.mouse[1]/(board_size//8)), int(self.mouse[0]/(board_size//8)))
                                if mouse_coord[1] <= 1 and mouse_coord[0] >= 6:
                                    self.move_to_play = self.temp_var["choices"][mouse_coord[0]*2-mouse_coord[1]-11] #Transform click location in move index
                                else :
                                    self.move_to_play = "Cancel" #Cancel promotion

                    elif self.settings[self.board.turn] == "bot": #Check if it's the bot turn
                        self.move_to_play = self.board.choose_best_move(1) #Play the move

                    elif self.settings[self.board.turn] == "random": #Checks if the round is to be played randomly
                        self.move_to_play = random.choice(self.board.get_all_possible_moves()) #Play the move

        if self.move_to_play != None:
            if self.move_to_play == "Cancel":
                self.sub_state = None
                self.temp_var = {}
                self.move_to_play = None
            else :
                self.board = self.board.move(self.move_to_play)
                self.sub_state = None
                self.temp_var = {}
                self.move_to_play = None
        
        surface = self.draw_board(self.mouse)
        if self.board.get_state() != "Running":
            surface = self.draw_pop_up(self.board.get_state(), surface)
        elif self.sub_state == "promotion":
            surface = self.promotion_choice(surface, self.mouse)
        return surface

def start_a_game(settings = ("player", "bot"), bsd = "white", bsz = 480, board = "start", pieces_style = "cburnett", board_style = "brown"):
    global board_side
    global board_size
    board_side = bsd
    board_size = (bsz//8)*8

    #Load piece's sprites
    sprites = {i : None for i in ["K", "P", "N", "B", "R", "Q", "k", "p", "n", "b", "r", "q"]}
    for i in sprites:
        sprites[i] = pygame.image.load(f"asset/pieces/{pieces_style}/{('b' if i.islower() else 'w')+i.upper()}.png")
        sprites[i] = pygame.transform.smoothscale(sprites[i], (int(sprites[i].get_width() * (board_size//8)/max(sprites[i].get_size())), int(sprites[i].get_height() * (board_size//8)/max(sprites[i].get_size()))))

    #Load Board
    sprites["Board"] = pygame.image.load(f"asset/boards/{board_style}.png")
    sprites["Board"] = pygame.transform.scale(sprites["Board"], (board_size, board_size))

    #Initialise the window
    pygame.init()
    pygame.display.set_caption("little-chess-game")
    pygame.display.set_icon(sprites["N"])
    window_surface = pygame.display.set_mode((board_size, board_size))

    running = True
    clock = pygame.time.Clock()
    board = DisplayBoard(chess.Board(board), board_side, board_size, settings, sprites, (0, 0))

    while running :
        pygame.display.flip()
        clock.tick(60)
        print(f"FPS : {round(clock.get_fps(), 2)}")
        new_events = pygame.event.get()
        if not new_events:
            new_events.append(pygame.event.Event(0))
        for event in new_events:
            if event.type == pygame.QUIT:
                running = False
        
        if running:
            window_surface.blit(board.handle_events(new_events), board.pos)

if __name__ == "__main__":

    #Creation of the tkinter setting window
    
    size = (600, 170)
    window = tk.Tk()
    window.title("Game settings")
    window.geometry(f"{size[0]}x{size[1]}")
    window.resizable(False, False)
    window.iconphoto(True, tk.PhotoImage(file = "asset/pieces/cburnett/wN.png"))
    window.columnconfigure(0, weight=1)
    window.rowconfigure(0, weight = 1)
    window.rowconfigure(1, weight = 1)
    window.rowconfigure(2, weight = 1)

    row1 = tk.Frame(window)
    row1.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
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
    frame5.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
    frame5.columnconfigure(1, weight=1)

    frame6 = tk.LabelFrame(window, text = "Style")
    frame6.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
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
        arg = ((liste1.get(liste1.curselection()[0]),liste2.get(liste2.curselection()[0])), liste3.get(liste3.curselection()[0]), int(size_set.get()), fen_entry.get(), pieces_style_list.get(), board_style_list.get())
        window.destroy()
        start_a_game(*arg)

    tk.Button(frame4, text="Create", command = create).pack(fill=tk.X, expand=True)

    tk.Label(frame5, text = "Fen : ").grid(row=0, column=0, sticky="w")

    fen_entry = tk.Entry(frame5)
    fen_entry.grid(row=0, column=1, sticky="ew")
    fen_entry.insert(0, "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
    
    tk.Label(frame6, text = "Pieces : ").grid(row=0, column=0, sticky="w")

    pieces_style_list = ttk.Combobox(frame6, values=os.listdir("asset/pieces"), state="readonly")
    pieces_style_list.grid(row=0, column=1, sticky="ew")
    pieces_style_list.current(os.listdir("asset/pieces").index('cburnett'))

    tk.Label(frame6, text = "Board : ").grid(row=0, column=2, sticky="w")

    board_style_list = ttk.Combobox(frame6, state="readonly", values=list(map(lambda x: x.split(".")[0], os.listdir("asset/boards"))))
    board_style_list.grid(row=0, column=3, sticky="ew")
    board_style_list.current(list(map(lambda x: x.split(".")[0], os.listdir("asset/boards"))).index('brown'))

    window.mainloop()