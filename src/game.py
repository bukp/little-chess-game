import random
import threading
import time
import pygame
import settings
import chess
import connection
import pyperclip
from tkinter import filedialog

DEBUG = False

MCAST_GROUP = ("239.1.2.3", 55555)

DEFAULT_SETTINGS = {
  "graphics": {
    "pieces_style": "cburnett",
    "board_style": "brown",
    "bsd": "auto",
    "bsz": 480
  },
  "game": {
    "settings": [
      "player",
      "player"
    ],
    "clock": "False",
    "times": [
      "10m",
      "10m"
    ],
    "address": [
      "127.0.0.1",
      "127.0.0.1"
    ],
    "port": [
      "54321",
      "55555"
    ],
    "board": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
  }
}

class DisplayBoard:

    def __init__(self,parent, settings = ("player", "bot"), address = ("127.0.0.1", "127.0.0.1"), port = ("54321", "54321"), bsd = "auto", bsz = 480, board = "start", clock = False, times = (900, 900), pieces_style = "cburnett", board_style = "brown", pos = (0, 0)):
        
        self.parent = parent
        self.settings = settings
        self.pos = pos
        self.clock_enabled = clock == "True"
        self.times = [i for i in times]
        for i in range(len(self.times)):
            self.times[i] = self.times[i].replace("s", "")
            if "m" in self.times[i]:
                self.times[i] = int("0"+self.times[i].split("m")[0])*60+int("0"+self.times[i].split("m")[1])
            else :
                self.times[i] = int(self.times[i])
        self.connections = [None, None]

        self.handling_methods = [{
            "player" : self.handle_player,
            "remote player" : self.handle_remote_player,
            "bot" : self.handle_bot,
            "random" : self.handle_random,
        }[self.settings[i]] for i in range(2)]

        self.address = address
        self.port = port
        for i in range(2):
            self.connect(i)
        
        self.update_graphics(bsd, bsz, pieces_style, board_style)

        self.mouse = (0, 0)
        self.board = chess.Board(board)
        self.move_to_play = None
        self.board_state = None
        self.page = "current"
        self.sub_state = None
        self.temp_var = {}
        self.thread = None

        self.starting_time = time.time()
    
    def connect(self, i):
        """Be careful, this do not disconnect before connecting"""
        if self.settings[i] == "remote player" and self.address[i] != "":
            self.connections[i] = connection.Connection(i == 0, self.address[i], int(self.port[i]), DEBUG)

    def update_graphics(self, bsd = "white", bsz = 480, pieces_style = "cburnett", board_style = "brown"):
        
        if bsd == "auto":
            if self.settings[1] == "player" and self.settings[0] != "player":
                bsd = "black"
            else :
                bsd = "white"
        self.board_side = bsd
        self.board_size = (bsz//8)*8
        #Load piece's sprites
        self.sprites = {i : None for i in ["K", "P", "N", "B", "R", "Q", "k", "p", "n", "b", "r", "q"]}
        for i in self.sprites:
            self.sprites[i] = pygame.image.load(f"asset/pieces/{pieces_style}/{('b' if i.islower() else 'w')+i.upper()}.png")
            self.sprites[i] = pygame.transform.smoothscale(self.sprites[i], (int(self.sprites[i].get_width() * (bsz//8)/max(self.sprites[i].get_size())), int(self.sprites[i].get_height() * (bsz//8)/max(self.sprites[i].get_size()))))

        #Load Board
        self.sprites["Board"] = pygame.image.load(f"asset/boards/{board_style}.png")
        self.sprites["Board"] = pygame.transform.scale(self.sprites["Board"], (bsz, bsz))

    def pos_to_coord(self, tup):
        """Convert pixels (mouse for example) coordinates into row/column coordinates"""
        board_side = self.board_side
        if board_side == "alternate":
            board_side = "white" if self.board.turn == 0 else "black"

        if board_side == "white":
            return (7-int(tup[1]/(self.board_size//8)), int(tup[0]/(self.board_size//8)))
        elif board_side == "black" :
            return (int(tup[1]/(self.board_size//8)), 7-int(tup[0]/(self.board_size//8)))

    def coord_to_pos(self ,tup):
        """Convert row/column coordinates into pixels coordinates"""
        board_side = self.board_side
        if board_side == "alternate":
            board_side = "white" if self.board.turn == 0 else "black"

        if board_side == "white":
            return ((self.board_size//8)*tup[1], (self.board_size//8)*7-(self.board_size//8)*tup[0])
        elif board_side == "black" :
            return ((self.board_size//8)*7-(self.board_size//8)*tup[1], (self.board_size//8)*tup[0])

    def draw_board(self, mouse_pos : tuple):
        """Draw the board"""
        board_surface = pygame.Surface((self.board_size, self.board_size))

        if self.page == "current":
            held_piece = self.temp_var["held_piece"] if "held_piece" in self.temp_var else None
            held_piece_moves = self.temp_var["held_piece_moves"] if "held_piece_moves" in self.temp_var else []
            last_move = self.board.last_move
            board = self.board
        else :
            held_piece = None
            held_piece_moves = []

            if type(self.page) == int:
                board = chess.Board(self.board.fen_list[self.page])
                last_move = self.board.move_list[self.page-1] if self.page >= 1 else None
            else :
                board = self.board
                last_move = self.board.last_move

        board_surface.blit(self.sprites["Board"], (0, 0))
        for row in range(8):
            for col in range(8):
                #Draw held piece effets 
                if (row, col) in held_piece_moves or (row, col) == held_piece:
                    cell_surface = pygame.Surface((self.board_size//8, self.board_size//8), pygame.SRCALPHA)
                    color = (0, 100, 255, 100)
                    if held_piece == (row, col):
                        color = color[:3]+(50,)
                        cell_surface.fill(color)
                    elif self.pos_to_coord(mouse_pos) == (row, col) or held_piece == (row, col):
                        cell_surface.fill(color)
                    else :
                        if board[row, col] != None:  # Draw circles where the piece can go (full if the square is empty, else empty to allow the user to see the piece)
                            pygame.draw.circle(cell_surface, color, (self.board_size//16, self.board_size//16), self.board_size//16, self.board_size//96)
                        else :
                            pygame.draw.circle(cell_surface, color, (self.board_size//16, self.board_size//16), self.board_size//48)
                    board_surface.blit(cell_surface, self.coord_to_pos((row, col)))
                
                elif last_move != None and (row, col) in last_move:
                    color = (0, 180, 0, 75)
                    cell_surface = pygame.Surface((self.board_size//8, self.board_size//8), pygame.SRCALPHA)
                    cell_surface.fill(color)
                    board_surface.blit(cell_surface, self.coord_to_pos((row, col)))

                if (row, col) != held_piece and board[row, col] != None:  # Draw the piece unless it's held (sprites taken from lichess)
                    board_surface.blit(self.sprites[board[row, col].letter.lower() if board[row, col].color == 1 else board[row, col].letter], self.coord_to_pos((row, col)))

        if held_piece != None: # If the piece is hels, draw it under the mouse
            board_surface.blit(self.sprites[board[held_piece].letter.lower() if board[held_piece].color == 1 else board[held_piece].letter], (mouse_pos[0] - self.board_size//16, mouse_pos[1] - self.board_size//16))
        return board_surface

    def promotion_choice(self, surface, mouse_pos):
        """Draw promotion window"""
        pygame.draw.rect(surface, (255, 255, 255), pygame.Rect(0, 0, self.board_size//4, self.board_size//4))
        mouse_pos = (7-mouse_pos[1]//(self.board_size//8), mouse_pos[0]//(self.board_size//8))
        if 0 <= mouse_pos[1] <= 1 and 7 >= mouse_pos[0] >= 6 :
            pygame.draw.rect(surface, (175, 175, 175), pygame.Rect((self.board_size//8)*mouse_pos[1], ((self.board_size//8)*7)-(self.board_size//8)*mouse_pos[0], (self.board_size//8), (self.board_size//8)))
        d = {"Q" : (0, 0), "R" : ((self.board_size//8), 0), "B" : (0, (self.board_size//8)), "N" : ((self.board_size//8), (self.board_size//8))}
        for i in d:
            surface.blit(self.sprites[i.lower() if self.board.turn == 1 else i], d[i])
        return surface

    def draw_pop_up(self, text, surface):
        """Draw end game popup"""
        grey_surface = pygame.Surface((self.board_size, self.board_size))
        grey_surface.fill((50, 50, 50))
        grey_surface.set_alpha(125)
        surface.blit(grey_surface, (0, 0))
        cell_size = self.board_size//8
        pygame.draw.rect(surface, (255, 255, 255), pygame.Rect(cell_size*2, cell_size*3, cell_size*4, cell_size*2))
        pygame.draw.rect(surface, (0, 0, 0), pygame.Rect(cell_size*2, cell_size*3, cell_size*4, cell_size*2), max(1, int(3*self.board_size/480)))

        text1 = font.render(text[0], True, (0, 0, 0), (255, 255, 255))
        coef = int(cell_size*9/10)/max(text1.get_height(), text1.get_width()//4)
        surf = pygame.Surface(text1.get_size())
        surf.blit(text1, (0, 0))
        text1 = pygame.transform.smoothscale(surf, (int(surf.get_width()*coef), int(surf.get_height()*coef)))

        text2 = font.render(text[1], True, (0, 0, 0), (255, 255, 255))
        coef = int(cell_size*7/10)/max(text2.get_height(), text2.get_width()//4)
        surf = pygame.Surface(text2.get_size())
        surf.blit(text2, (0, 0))
        text2 = pygame.transform.smoothscale(surf, (int(surf.get_width()*coef), int(surf.get_height()*coef)))

        text = pygame.Surface((int(cell_size*4*9/10), int(cell_size*2*9/10)))
        text.fill((255, 255, 255))
        text.blit(text1, (text.get_width()/2 - text1.get_width()/2,text.get_height()/4 - text1.get_height()/2))
        text.blit(text2, (text.get_width()/2 - text2.get_width()/2,text.get_height()*3/4 - text2.get_height()/2))
        surface.blit(text, (self.board_size//2-text.get_width()/2, self.board_size//2-text.get_height()/2))
        return surface

    def handle_player(self, event):
        if self.board_state == "Running":
            if self.sub_state == None:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: #Get the left click and places the piece in the hand if there is one at the click location
                    pos = self.pos_to_coord(self.mouse)
                    if self.board[pos] != None and self.board[pos].color == self.board.turn:
                        self.temp_var["held_piece"] = pos
                        self.temp_var["held_piece_moves"] = []
                        lis = self.board.get_moves_starting_with(self.temp_var["held_piece"])
                        for i in lis:
                            self.temp_var["held_piece_moves"].append(i[1])

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3: #Drop the piece if right click
                    self.temp_var = {}

                if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and "held_piece" in self.temp_var:
                    moves, lis = self.board.get_moves_starting_with(self.temp_var["held_piece"]), [] #Get all possible moves
                    for i in moves: #Get all moves ending at the click location
                        lis.append(i[1])

                    choices = []
                    if self.pos_to_coord(self.mouse) in lis:
                        for i in moves:
                            if (i[0], i[1]) == (self.temp_var["held_piece"], self.pos_to_coord(self.mouse)):
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
                    mouse_pos = (7-self.mouse[1]//(self.board_size//8), self.mouse[0]//(self.board_size//8))
                    if 0 <= mouse_pos[1] <= 1 and 7 >= mouse_pos[0] >= 6 :
                        self.move_to_play = self.temp_var["choices"][mouse_pos[0]*2-mouse_pos[1]-11] #Transform click location in move index
                    else :
                        self.move_to_play = "Cancel" #Cancel promotion

    def handle_remote_player(self, event):
        if self.board_state == "Running":
            if self.thread == None and self.connections[self.board.turn] != None and self.connections[self.board.turn].connected:
                def waiting_other_player():
                    if self.board.last_move == None:
                        message = "0;;"
                    else:
                        message = f"{len(self.board.fen_list)};{str(self.board.last_move[0][0])+str(self.board.last_move[0][1])+str(self.board.last_move[1][0])+str(self.board.last_move[1][1])+(str(self.board.last_move[2]) if len(self.board.last_move)>2 else '')};{self.board.to_complete_fen()};{self.times[(self.board.turn+1)%2]+1}"

                    last_time = 0
                    while True:
                        if not self.connections[self.board.turn].alive:
                            self.thread = None
                            return
                        
                        if time.time() - last_time > 5:
                            self.connections[self.board.turn].send(message)
                            last_time = time.time()

                        last_message = self.connections[self.board.turn].last_message.split(";")
                        if last_message[0].isdigit():
                            if int(last_message[0]) > len(self.board.fen_list)+1 or int(last_message[0]) < len(self.board.fen_list)-1:
                                self.end_all_connections("ended;error")
                                self.board_state = ("Error", "-")
                                self.thread = None
                                return

                            if int(last_message[0]) == len(self.board.fen_list)+1:
                                break

                        time.sleep(0.5)
                    
                    move = (int(last_message[1][0]), int(last_message[1][1])),(int(last_message[1][2]), int(last_message[1][3]))
                    if len(last_message[1]) > 4:
                        move = move + (last_message[1][4:],)
                    simulated_board = self.board.move(move)

                    if simulated_board.to_complete_fen() != last_message[2]:
                        self.end_all_connections("ended;error")
                        self.board_state = ("Error", "-")
                        return
                
                    self.move_to_play = move
                    self.times[self.board.turn] = int(last_message[3])
                    self.starting_time = time.time()

                    if simulated_board.get_state() != "Running":
                        self.connections[self.board.turn].close()
                    
                self.thread = threading.Thread(target = waiting_other_player, name="Waiting remote player to move", daemon = True)
                self.thread.start()

    def handle_bot(self, event):
        if self.board_state == "Running":
            if self.thread == None:
                def computing_move():
                    self.move_to_play = self.board.choose_best_move(1) #Play the move
                self.thread = threading.Thread(target = computing_move, name="Computing bot move", daemon=True)
                self.thread.start()
    
    def handle_connections(self):
        for i in range(len(self.connections)):
            if self.connections[i] != None:
                last_message = self.connections[i].last_message.split(";")
                if last_message[0] == "ended":

                    if last_message[1] == "error":
                        self.board_state = ("Error", "-")
                    
                    elif last_message[1] == "disconnected":
                        if i == 1:
                            self.board_state = ("White won by disconnection", "1 - 0")    
                        else :
                            self.board_state = ("Black won by disconnection", "0 - 1")
                    
                    elif last_message[1] == "timeout":
                        if i == 1:
                            self.board_state = ("White won by timeout", "1 - 0")
                        else :
                            self.board_state = ("Black won by timeout", "0 - 1")
                        self.times[i] = 0
                        self.starting_time = time.time()

                    elif last_message[1] == "resignation":
                        if i == 1:
                            self.board_state = ("White won by resignation", "1 - 0")
                        else :
                            self.board_state = ("Black won by resignation", "0 - 1")
                    
                    self.connections[i].close()

    def handle_random(self, event):
        if self.board_state == "Running":
            self.move_to_play = random.choice(self.board.get_all_possible_moves()) #Play the move
    
    def handle_events(self, events):
        """Main handler that call all the others, get an event list and return a surface to display on the window"""

        last_state = self.board_state

        if self.board_state == None:
            self.board_state = self.board.get_state()
        
        for i in range(len(self.connections)):
            if self.settings[i] == "remote player" and (self.connections[i] == None or not self.connections[i].connected):
                self.starting_time = time.time()
                break
        
        if self.board_state == "Running" and self.settings[self.board.turn] in ("player", "bot", "random"):
            if self.times[self.board.turn] < time.time() - self.starting_time and self.clock_enabled:
                self.board_state = (f"{'White' if self.board.turn == 1 else 'Black'} won by timeout", f"{int(self.board.turn == 1)} - {int(self.board.turn == 0)}")
                self.times[self.board.turn] = 0
                self.end_all_connections("ended;timeout")
        
        if self.board_state == "Running":
            self.handle_connections()

        for event in events:
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION): #Get mouse pos
                if not (self.pos[0] <= event.pos[0] < self.pos[0] + self.board_size and self.pos[1] <= event.pos[1] < self.pos[1] + self.board_size):
                    event = pygame.event.Event(pygame.MOUSEBUTTONUP, button = 1, pos = (-10, -10))
                self.mouse = (event.pos[0]-self.pos[0], event.pos[1]-self.pos[1])

            if event.type == pygame.MOUSEBUTTONDOWN and event.button in (1, 3): #Go back at current page
                self.page = "current"
            
            if event.type == pygame.KEYDOWN and event.key == (pygame.K_LEFT) or event.type == pygame.MOUSEWHEEL and event.y < 0:
                if type(self.page) == str:
                    self.page = len(self.board.fen_list) - 1
                else :
                    self.page = self.page - 1
            
            if event.type == pygame.KEYDOWN and event.key == (pygame.K_RIGHT) or event.type == pygame.MOUSEWHEEL and event.y > 0:
                if type(self.page) == int:
                    self.page = self.page + 1

            if type(self.page) == int:
                self.page = max(0, self.page) #Clamping page above 0
                if self.page >= len(self.board.fen_list) : #Clamping under the current page
                    self.page = "current"

            self.handling_methods[self.board.turn](event) #Call differents handling functions for players, bots, ...

        if self.board_state != "Running":
            self.move_to_play = None
        if self.move_to_play != None:
            if self.move_to_play == "Cancel":
                self.sub_state = None
                self.temp_var = {}
                self.move_to_play = None
                self.thread = None
                self.page = "current"
            else :
                #Switching clock
                if self.clock_enabled:
                    self.times[self.board.turn] = max(self.times[self.board.turn] - int(time.time() - self.starting_time), 0)
                    self.starting_time = time.time()

                self.board = self.board.move(self.move_to_play)
                self.board_state = self.board.get_state()
                if self.board_state != "Running":
                    self.end_all_connections(f"{len(self.board.fen_list)};{str(self.board.last_move[0][0])+str(self.board.last_move[0][1])+str(self.board.last_move[1][0])+str(self.board.last_move[1][1])+(str(self.board.last_move[2]) if len(self.board.last_move)>2 else '')};{self.board.to_complete_fen()};{self.times[(self.board.turn+1)%2]+1}")
                self.sub_state = None
                self.temp_var = {}
                self.move_to_play = None
                self.thread = None
                self.page = "current"

        if self.board_state != "Running" and self.board_state != last_state:
            self.page = "popup"
        
        surface = self.draw_board(self.mouse)
        
        if self.page == "popup":
            surface = self.draw_pop_up(self.board_state, surface)
        
        if self.sub_state == "promotion":
            surface = self.promotion_choice(surface, self.mouse)
        
        return surface

    def filter_events(self, events):
        return events

    def import_pgn(self, pgn):
        """Execute moves from a PGN format string.
        Should be used only at the moment the object is created"""

        pgn = [i for i in pgn.split(" ") if "." not in i and i not in ("1-0", "0-1", "½-½")]
        for i in pgn:
            self.board = self.board.move(self.board.make_unreadeable(i))

    def export_pgn(self):
        if self.board.to_pgn() == None:
            return
        diag = filedialog.asksaveasfile("w", filetypes = (("Portable Game Notation", "*.pgn"),), defaultextension = ".pgn")
        if diag == None:
            return
        with open(diag.name, "w", encoding="utf-8") as file:
            file.write(self.board.to_pgn())

    def end_all_connections(self, message = "ended;disconnected", wait = True):
        for i in self.connections:
            if i != None and i.connected:
                threading.Thread(target = i.end_connection, name="Ending connection", args=[message, wait], daemon = True).start()
            elif i != None:
                i.close()

class Label:

    def __init__(self, window, text, pos, background_color = (40, 40, 40), text_color = (255, 255, 255)):
        self.window = window
        self.text = text
        self.size = pos[2:]
        self.pos = pos[:2]
        self.background_color = background_color
        self.text_color = text_color
        self.is_over = False

        surface = font.render(self.text, True, self.text_color, self.background_color)
        text_surface = pygame.Surface(surface.get_size())
        text_surface.blit(surface, (0, 0))
        coef = max(text_surface.get_width()/self.size[0], text_surface.get_height()/self.size[1])/(9/10)
        text_surface = pygame.transform.smoothscale(text_surface, (text_surface.get_width()//coef, text_surface.get_height()//coef))
        self.text_surface = pygame.Surface(self.size)
        self.text_surface.fill(self.background_color)
        self.text_surface.blit(text_surface, (int(self.size[0]/2-text_surface.get_width()/2),int(self.size[1]/2-text_surface.get_height()/2)))
        
    def handle_events(self, events):
        return self.text_surface.copy()
    
    def filter_events(self, events):
        #Mask preventing from clicking on two objects at the same time
        for i in range(len(events)):
            if events[i].type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                if self.pos[0] <= events[i].pos[0] < self.pos[0] + self.size[0] and self.pos[1] <= events[i].pos[1] < self.pos[1] + self.size[1]:
                    events[i] = pygame.event.Event(pygame.MOUSEBUTTONUP, button = 1, pos = (-10, -10))
        return events

class Button:

    def __init__(self, window, text, pos, action, background_color = (40, 40, 40), text_color = (255, 255, 255), press_button = True):
        self.window = window
        self.text = text
        self.size = pos[2:]
        self.pos = pos[:2]
        self.action = action
        self.background_color = background_color
        self.text_color = text_color
        self.state = "UP"
        self.is_over = False
        self.press_button = press_button

        surface = font.render(self.text, True, self.text_color, self.background_color)
        text_surface = pygame.Surface(surface.get_size())
        text_surface.blit(surface, (0, 0))
        coef = max(text_surface.get_width()/self.size[0], text_surface.get_height()/self.size[1])/(9/10)
        text_surface = pygame.transform.smoothscale(text_surface, (text_surface.get_width()//coef, text_surface.get_height()//coef))
        self.text_surface = pygame.Surface(self.size)
        self.text_surface.fill(self.background_color)
        self.text_surface.blit(text_surface, (int(self.size[0]/2-text_surface.get_width()/2),int(self.size[1]/2-text_surface.get_height()/2)))
        
    def handle_events(self, events):

        for event in events:

            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION): #Get mouse pos
                pointer = event.pos
                if self.pos[0] <= pointer[0] < self.pos[0] + self.size[0] and self.pos[1] <= pointer[1] < self.pos[1] + self.size[1]:
                    self.is_over = True
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button in (1, 3):
                        self.state = "DOWN"
                    elif event.type == pygame.MOUSEBUTTONUP and event.button in (1, 3):
                        if self.state == "DOWN":
                            self.state = "UP"
                            self.action(self.window)
                        self.state = "UP"
                else:
                    self.is_over = False
                    self.state = "UP"
        
        surface = self.text_surface.copy()
        if self.is_over:
            if self.state == "DOWN":
                color = (0, 0, 0)
            else:
                color = (255, 255, 255)
            surf = pygame.Surface(self.text_surface.get_size())
            surf.fill(color)
            surf.set_alpha(25)
            surface.blit(surf, (0, 0))
        if self.state == "DOWN":
            surf = pygame.Surface(self.size, pygame.SRCALPHA)
            if self.press_button:
                surface = pygame.transform.smoothscale(surface, (int(surface.get_width()*92/100), int(surface.get_height()*92/100)))
            surf.blit(surface, (int(self.size[0]/2-surface.get_width()/2),int(self.size[1]/2-surface.get_height()/2)))
            surface = surf
        return surface
    
    def filter_events(self, events):
        #Mask preventing from clicking on two objects at the same time
        for i in range(len(events)):
            if events[i].type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                if self.pos[0] <= events[i].pos[0] < self.pos[0] + self.size[0] and self.pos[1] <= events[i].pos[1] < self.pos[1] + self.size[1]:
                    events[i] = pygame.event.Event(pygame.MOUSEBUTTONUP, button = 1, pos = (-10, -10))
        return events

class Menu:
    
    def __init__(self, window, text, pos, buttons, background_color = (40, 40, 40), text_color = (255, 255, 255)):
        self.window = window
        self.text = text
        self.real_size = pos[2:]
        self.size = self.real_size[0], self.real_size[1]
        self.pos = pos[:2]
        self.background_color = background_color
        self.text_color = text_color
        self.is_really_over = False
        self.is_over = False

        self.flags = []
        self.buttons = []
        for i in range(len(buttons)):
            self.buttons.append(Button(self.window, buttons[i][0], (self.pos[0], self.pos[1]+(i+1)*(self.real_size[1]+5)-5, self.real_size[0], self.real_size[1]), buttons[i][1], press_button=False))
            if len(buttons[i]) > 2:
                self.flags.append(buttons[i][2])
            else :
                self.flags.append("")
        
        surface = font.render(self.text, True, self.text_color, self.background_color)
        text_surface = pygame.Surface(surface.get_size())
        text_surface.blit(surface, (0, 0))
        coef = max(text_surface.get_width()/self.real_size[0], text_surface.get_height()/self.real_size[1])/(9/10)
        text_surface = pygame.transform.smoothscale(text_surface, (text_surface.get_width()//coef, text_surface.get_height()//coef))
        self.text_surface = pygame.Surface(self.real_size)
        self.text_surface.fill(self.background_color)
        self.text_surface.blit(text_surface, (int(self.real_size[0]/2-text_surface.get_width()/2),int(self.real_size[1]/2-text_surface.get_height()/2)))
        
    def add_button(self, button):
        self.buttons.append(Button(self.window, button[0], (self.pos[0], self.pos[1]+(len(self.buttons)+1)*(self.real_size[1]+5)-5, self.real_size[0], self.real_size[1]), button[1], press_button=False))
        if len(button) > 2:
            self.flags.append(button[2])
        else :
            self.flags.append("")
            
    def remove_button(self, button_index):
        self.flags.pop(button_index)
        self.buttons.pop(button_index)
        if len(self.buttons)-1 >= button_index:
            for i in self.buttons[button_index:]:
                i.pos = i.pos[0], i.pos[1]-self.real_size[1]-5

    def get_button_with_flag(self, flag):
        if flag in self.flags:
            return self.buttons[self.flags.index(flag)]
    
    def remove_button_with_flag(self, flag):
        if flag in self.flags:
            self.remove_button(self.flags.index(flag))

    def handle_events(self, events):
        for event in events:
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION): #Get mouse pos
                pointer = event.pos
                if self.pos[0] <= pointer[0] < self.pos[0] + self.size[0] and self.pos[1] <= pointer[1] < self.pos[1] + self.size[1]:
                    self.is_over = True
                    if self.pos[0] <= pointer[0] < self.pos[0] + self.real_size[0] and self.pos[1] <= pointer[1] < self.pos[1] + self.real_size[1]:
                        self.is_really_over = True
                    else :
                        self.is_really_over = False
                else:
                    self.is_really_over = False
                    self.is_over = False
        
        if self.is_over:
            self.size = self.real_size[0], self.real_size[1] + (self.real_size[1] + 4) * len(self.buttons)
            surface = pygame.Surface(self.size)
            surface.fill((10, 10, 10))
            surface.blit(self.text_surface, (0, 0))
            if self.is_really_over:
                surf = pygame.Surface(self.text_surface.get_size())
                surf.fill((255, 255, 255))
                surf.set_alpha(25)
                surface.blit(surf, (0, 0))

            for i in range(len(self.buttons)):
                surface.blit(self.buttons[i].handle_events(events), (0, (self.real_size[1]+4) * (i+1)))
        else :
            surface = self.text_surface.copy()
            self.size = self.real_size
        return surface
    
    def filter_events(self, events):
        #Mask preventing from clicking on two objects at the same time
        for i in range(len(events)):
            if events[i].type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                if self.pos[0] <= events[i].pos[0] < self.pos[0] + self.size[0] and self.pos[1] <= events[i].pos[1] < self.pos[1] + self.size[1]:
                    events[i] = pygame.event.Event(pygame.MOUSEBUTTONUP, button = 1, pos = (-10, -10))
        return events

class Clock:
    
    def __init__(self, window, color, pos, background_color = (255, 255, 255), secondary_background_color = (100, 100, 100), text_color = (0, 0, 0)):
        self.window = window
        self.size = pos[2:]
        self.pos = pos[:2]
        self.color = color
        self.text_color = text_color
        self.background_color = background_color
        self.secondary_background_color = secondary_background_color
        self.last = ""
        
    def handle_events(self, events):
        
        if self.window.board.board.turn == self.color and self.window.board.board_state == "Running":
            background = self.background_color
        else :
            background = self.secondary_background_color

        t = self.window.board.times[self.color]
        if self.color == self.window.board.board.turn and self.window.board.board_state == "Running":
            t -= int(time.time() - self.window.board.starting_time)
        t = max(t, 0)
        text = f"{t//60}:{'0' if t % 60 < 10 else ''}{t % 60}"

        if self.last == (text, background):
            return self.text_surface
        
        self.last = text, background

        surface = font.render(text, True, self.text_color, background)
        text_surface = pygame.Surface(surface.get_size())
        text_surface.blit(surface, (0, 0))
        coef = max(text_surface.get_width()/self.size[0], text_surface.get_height()/self.size[1])/(9/10)
        text_surface = pygame.transform.smoothscale(text_surface, (text_surface.get_width()//coef, text_surface.get_height()//coef))
        self.text_surface = pygame.Surface(self.size)
        self.text_surface.fill(background)
        self.text_surface.blit(text_surface, (int(self.size[0]/2-text_surface.get_width()/2),int(self.size[1]/2-text_surface.get_height()/2)))
        
        return self.text_surface
    
    def filter_events(self, events):
        #Mask preventing from clicking on two objects at the same time
        for i in range(len(events)):
            if events[i].type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                if self.pos[0] <= events[i].pos[0] < self.pos[0] + self.size[0] and self.pos[1] <= events[i].pos[1] < self.pos[1] + self.size[1]:
                    events[i] = pygame.event.Event(pygame.MOUSEBUTTONUP, button = 1, pos = (-10, -10))
        return events

class MainWindow:

    def __init__(self, board_settings = None):

        self.running = True

        if board_settings == None:
            self.board_settings = settings.user_settings("graphics") | DEFAULT_SETTINGS["game"]
        else :
            self.board_settings = board_settings
        
        self.board_settings["parent"] = self
        self.board_settings["pos"] = (4, (self.board_settings["bsz"]//16))

        self.board = DisplayBoard(**self.board_settings)
        
        #Initialize pygame
        pygame.init()
        pygame.display.set_caption("little-chess-game")
        pygame.display.set_icon(pygame.image.load("asset/pieces/cburnett/bN.png"))

        #Initialize the font
        global font
        font = pygame.font.Font("asset/font.ttf", 300)

        self.refresh_ui()
        
        self.lan_game_list = []
        threading.Thread(target=self.listen_group_games, name="Listening group_conn for updates", daemon=True).start()

    def refresh_ui(self):

        self.board_settings["pos"] = (4, (self.board_settings["bsz"]//16))
        self.board.pos = self.board_settings["pos"]

        self.components = []

        #Initialise the window
        self.window_surface = pygame.display.set_mode(((self.board.board_size)+8, (self.board.board_size*18//16 if self.board_settings["clock"] == "True" else self.board.board_size*17//16+5)))
        def restart(window : MainWindow):
            #Fermeture des sockets pour éviter des bugs comme la connection avec une socket inutilisée
            self.board.end_all_connections("ended;disconnected", False)
            window.board = DisplayBoard(**window.board_settings)
            self.game_id = None

        def game_settings(window : MainWindow):
            last_clock = window.board_settings["clock"]
            new_settings = settings.game_settings_window()
            if new_settings == None:
                return
            #Fermeture des sockets pour éviter des bugs comme la connection avec une socket inutilisée
            self.board.end_all_connections("ended;disconnected", False)
            lan = new_settings[1]
            new_settings = new_settings[0]
            for i in new_settings:
                window.board_settings[i] = new_settings[i]

            if lan:
                window.board_settings["address"] = ["", ""]
                threading.Thread(target=window.offer_group_game, args=[new_settings], name="Offering group game on LAN", daemon=True).start()

            window.board = DisplayBoard(**window.board_settings)
            if window.board_settings["clock"] != last_clock:
                window.refresh_ui()
        
        self.components.append(Menu(self, "New Game", (self.board.pos[0], 4, (self.board.board_size//4)-2, (self.board.board_size//16)-8),[("Restart", restart), ("Custom Game", game_settings)]))
        
        self.components.append(Menu(self, "Join Game", (self.board.pos[0]+self.board.board_size//4+2, 4, (self.board.board_size//4)-4, (self.board.board_size//16)-8), []))

        def import_pgn(window : MainWindow):
            diag = filedialog.askopenfile("r", defaultextension="*.pgn")
            if diag == None:
                return
            with open(diag.name, "r", encoding="utf-8") as file:
                pgn = file.read()
            
            if "\n\n" in pgn:
                pgn = pgn.split("\n\n")[1]
            
            pgn = pgn.replace("\n", " ")
            
            window.board.delete()
            window.board = DisplayBoard(**window.board_settings)
            window.board.import_pgn(pgn)
        
        def export(window : MainWindow):
            window.board.export_pgn()
        
        def get_fen(window : MainWindow):
            pyperclip.copy(window.board.board.to_complete_fen())
        
        self.components.append(Menu(self, "Files", (self.board.pos[0]+self.board.board_size*2//4+2, 4, (self.board.board_size//4)-4, (self.board.board_size//16)-8), [("Import", import_pgn), ("Export", export), ("FEN", get_fen)]))
        
        def graphics_settings(window : MainWindow):
            last_size = window.board.board_size
            new_settings = settings.graphics_settings_window()
            if new_settings == None:
                return
            window.board.update_graphics(**new_settings)
            for i in new_settings:
                window.board_settings[i] = new_settings[i]
            if window.board.board_size != last_size:
                window.refresh_ui()

        self.components.append(Menu(self, "Settings", (self.board.pos[0]+self.board.board_size*3//4+2, 4, (self.board.board_size//4)-2, (self.board.board_size//16)-8), [("Graphics", graphics_settings)]))
        
        if self.board_settings["clock"] == "True":

            self.components.append(Clock(self, 0, (4, self.board.board_size*17/16+4, self.board.board_size//8*2, self.board.board_size//16-8)))

            self.components.append(Clock(self, 1, (self.board.board_size*6//8+4, self.board.board_size*17/16+4, self.board.board_size//8*2, self.board.board_size//16-8)))

            self.components.append(Label(self, "White", (self.board.board_size*2//8+8, self.board.board_size*17/16+4, self.board.board_size//8*2-12, self.board.board_size//16-8), (10, 10, 10)))
            
            self.components.append(Label(self, "Black", (self.board.board_size*4//8+12, self.board.board_size*17/16+4, self.board.board_size//8*2-12, self.board.board_size//16-8), (10, 10, 10)))

            self.components.append(Label(self, "-", (self.board.board_size*4//8-4, self.board.board_size*17/16+4, 16, self.board.board_size//16-8), (10, 10, 10)))

    def listen_group_games(self):
        self.group_conn = connection.GroupConnection(MCAST_GROUP, DEBUG)
        self.group_offers = {}
        self.game_id = None
        self.old_game_id = set()
        while self.running:
            if self.group_conn.last_message != None:
                message = self.group_conn.last_message[0].split(";")
                id = int(message[0])
                if message[1] == "offer" and id not in self.old_game_id:
                    self.group_offers[id] = {
                        "address" : self.group_conn.last_message[1][0],
                        "game settings" : {i.split("=")[0] : i.split("=")[1].split(",") if "," in i.split("=")[1] else i.split("=")[1] for i in message[2:]},
                        "last update" : time.time(),
                    }
                    self.group_offers[id]["game settings"]["address"] = [self.group_conn.last_message[1][0]] * 2
                    if self.components[1].get_button_with_flag(id) == None:
                        self.components[1].add_button((self.group_offers[id]["address"], lambda x, id=id: x.accept_group_game(id), id))
                    self.group_conn.last_message = None
                elif message[1] == "accept":
                    if self.game_id == id:
                        self.game_id = None
                        self.board_settings["address"] = [self.group_conn.last_message[1][0]] * 2
                        self.board.address = [self.group_conn.last_message[1][0]] * 2
                        self.board.connect(0)
                        self.board.connect(1)
                    elif id in self.group_offers:
                        del self.group_offers[id]
                        self.components[1].remove_button_with_flag(id)
            for id in self.group_offers.copy():
                if self.group_offers[id]["last update"] < time.time() - 5:
                    del self.group_offers[id]
                    self.components[1].remove_button_with_flag(id)
            time.sleep(0.1)

        self.group_conn.close()
    
    def accept_group_game(self, id):
        last_clock = self.board_settings["clock"]
        for i in self.group_offers[id]["game settings"]:
            self.board_settings[i] = self.group_offers[id]["game settings"][i]
        self.board = DisplayBoard(**self.board_settings)

        if self.board_settings["clock"] != last_clock:
            self.refresh_ui()
        
        del self.group_offers[id]
        self.components[1].remove_button_with_flag(id)

        def accept(id = id):
            while not self.board.connections[self.board_settings["settings"].index("remote player")].connected:
                self.group_conn.group_send(f"{id};accept")
                time.sleep(0.5)
        threading.Thread(target=accept, name="Accepting group game", daemon=True).start()

    def offer_group_game(self, settings):
        id = random.randint(10000000, 99999999)
        self.game_id = id
        self.old_game_id.add(id)
        settings = {i : settings[i] if type(settings[i]) in (int, str) else [j for j in settings[i]] for i in settings}

        if settings["settings"][0] == settings["settings"][1] == "remote player":
            return

        if settings["settings"][0] == "remote player":
            settings["settings"][0] = "player"
            settings["settings"][1] = "remote player"
            settings["address"][1] = ""
            settings["port"][1] = settings["port"][0]
        
        elif settings["settings"][1] == "remote player":
            settings["settings"][1] = "player"
            settings["settings"][0] = "remote player"
            settings["address"][0] = ""
            settings["port"][0] = settings["port"][1]

        message = f"{id};offer;"
        for i in settings:
            message += f"{i}={settings[i]};".replace("(", "").replace(")", "").replace("[", "").replace("]", "").replace("'", "").replace(", ", ",")
        message = message[:-1]
        if DEBUG:
            print(message)
        while self.game_id == id:
            self.group_conn.group_send(message)
            time.sleep(0.6)

    def run(self, fps = 60):

        clock = pygame.time.Clock()

        while self.running :
            pygame.display.flip()
            clock.tick(fps)
            self.window_surface.fill((10, 10, 10))
            new_events = pygame.event.get()
            if not new_events:
                new_events.append(pygame.event.Event(0))
            
            #Close the window if the user click the cross
            for event in new_events:
                if event.type == pygame.QUIT:
                    self.board.end_all_connections("ended;disconnected")
                    self.running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_d:
                    print("\nActive threads :")
                    for i in threading.enumerate():
                        print(" - "+i.name)
                    print("\nBoard settings : ", self.board_settings)
                    print("\nGame id :", self.game_id)
                    print("\nGame offers : ")
                    for i in self.group_offers:
                        print(" -", i, self.group_offers[i])
                    print("\n")

            if not self.running:
                break
            
            rendering_list = []

            for component in self.components[::-1]:
                rendering_list.append((component.handle_events(new_events), component.pos))
                new_events = component.filter_events(new_events)
            
            rendering_list.append((self.board.handle_events(new_events), self.board.pos))

            for i in rendering_list[::-1]:
                self.window_surface.blit(*i)

if __name__ == "__main__":
    MainWindow().run()