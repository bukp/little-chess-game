import random
import threading
import time
import socket
import pygame
import settings
import chess
import os
from tkinter import filedialog

DEBUG = False

DEFAULT_SETTINGS = {"settings": ["player", "bot"], "options": [{"address": "127.0.0.1", "port": "54321"}, {"address": "127.0.0.1", "port": "54321"}], "bsd": "white", "bsz": 480, "board": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", "pieces_style": "cburnett", "board_style": "brown"}

class DisplayBoard:

    def __init__(self,parent, settings = ("player", "bot"), options = (), bsd = "white", bsz = 480, board = "start", pieces_style = "cburnett", board_style = "brown", pos = (0, 0)):
        
        self.parent = parent
        self.board_side = bsd
        self.board_size = (bsz//8)*8
        self.settings = settings
        self.pos = pos

        #Load piece's sprites
        self.sprites = {i : None for i in ["K", "P", "N", "B", "R", "Q", "k", "p", "n", "b", "r", "q"]}
        for i in self.sprites:
            self.sprites[i] = pygame.image.load(f"asset/pieces/{pieces_style}/{('b' if i.islower() else 'w')+i.upper()}.png")
            self.sprites[i] = pygame.transform.smoothscale(self.sprites[i], (int(self.sprites[i].get_width() * (bsz//8)/max(self.sprites[i].get_size())), int(self.sprites[i].get_height() * (bsz//8)/max(self.sprites[i].get_size()))))

        #Load Board
        self.sprites["Board"] = pygame.image.load(f"asset/boards/{board_style}.png")
        self.sprites["Board"] = pygame.transform.scale(self.sprites["Board"], (bsz, bsz))

        self.connections = [None, None]
        for i in range(2):
            if self.settings[i] == "remote player":
                self.connections[i] = Connection(i == 0, options[i]["address"], int(options[i]["port"]), DEBUG)
        
        self.handling_methods = [{
            "player" : self.handle_player,
            "remote player" : self.handle_remote_player,
            "bot" : self.handle_bot,
            "random" : self.handle_random,
        }[self.settings[i]] for i in range(2)]
        
        self.mouse = (0, 0)
        self.board = chess.Board(board)
        self.move_to_play = None
        self.board_state = None
        self.page = "current"
        self.sub_state = None
        self.temp_var = {}
        self.thread = None

    def pos_to_coord(self, tup):
        """Convert pixels (mouse for example) coordinates into row/column coordinates"""
        if self.board_side == "white":
            return (7-int(tup[1]/(self.board_size//8)), int(tup[0]/(self.board_size//8)))
        elif self.board_side == "black" :
            return (int(tup[1]/(self.board_size//8)), 7-int(tup[0]/(self.board_size//8)))

    def coord_to_pos(self ,tup):
        """Convert row/column coordinates into pixels coordinates"""
        if self.board_side == "white":
            return ((self.board_size//8)*tup[1], (self.board_size//8)*7-(self.board_size//8)*tup[0])
        elif self.board_side == "black" :
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
            if self.thread == None and self.connections[self.board.turn].connected:
                def waiting_other_player():
                    if self.board.last_move == None:
                        message = "0;;"
                    else:
                        message = f"{len(self.board.fen_list)};{str(self.board.last_move[0][0])+str(self.board.last_move[0][1])+str(self.board.last_move[1][0])+str(self.board.last_move[1][1])+(str(self.board.last_move[2]) if len(self.board.last_move)>2 else '')};{self.board.to_complete_fen()}"

                    last = 0
                    while True:

                        if not self.connections[self.board.turn].alive:
                            self.thread = None
                            return
                        
                        if time.time() - last > 5:
                            self.connections[self.board.turn].send(message)
                            last = time.time()

                        last_message = self.connections[self.board.turn].last_message.split(";")
                        if last_message[0].isdigit():
                            if int(last_message[0]) > len(self.board.fen_list)+1 or int(last_message[0]) < len(self.board.fen_list)-1:
                                self.connections[self.board.turn].end_connection()
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
                        self.connections[self.board.turn].end_connection()
                        self.thread = None
                        return
                
                    self.move_to_play = move
                    
                    if simulated_board.get_state() != "Running":
                        self.unconnect(self.board.turn)
                    
                self.thread = threading.Thread(target = waiting_other_player, daemon = True)
                self.thread.start()
        else :
            #Case of a game ending, we need to tell the other which don't know
            if self.thread == None and self.connections[self.board.turn].connected:
                self.thread = threading.Thread(target = self.connections[self.board.turn].end_connection, args=[f"{len(self.board.fen_list)};{str(self.board.last_move[0][0])+str(self.board.last_move[0][1])+str(self.board.last_move[1][0])+str(self.board.last_move[1][1])+(str(self.board.last_move[2]) if len(self.board.last_move)>2 else '')};{self.board.to_complete_fen()}"], daemon = True)
                self.thread.start()

    def handle_bot(self, event):
        if self.board_state == "Running":
            if self.thread == None:
                def computing_move():
                    self.move_to_play = self.board.choose_best_move(1) #Play the move
                self.thread = threading.Thread(target = computing_move)
                self.thread.start()
    
    def handle_random(self, event):
        if self.board_state == "Running":
            self.move_to_play = random.choice(self.board.get_all_possible_moves()) #Play the move
    
    def handle_events(self, events):
        last_state = self.board_state

        if self.board_state == None:
            self.board_state = self.board.get_state()

        for event in events:
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION): #Get mouse pos
                pointer = event.pos
                if self.pos[0] <= pointer[0] < self.pos[0] + self.board_size and self.pos[1] <= pointer[1] < self.pos[1] + self.board_size:
                    self.mouse = (pointer[0]-self.pos[0], pointer[1]-self.pos[1])
                else :
                    event = pygame.event.Event(pygame.MOUSEBUTTONUP, button = 1)
                    self.mouse = (self.pos[0]-10, self.pos[1]-10)

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

        if self.move_to_play != None:
            if self.move_to_play == "Cancel":
                self.sub_state = None
                self.temp_var = {}
                self.move_to_play = None
                self.thread = None
                self.page = "current"
            else :
                self.board = self.board.move(self.move_to_play)
                self.board_state = self.board.get_state()
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

    def import_pgn(self, pgn):
        """Execute moves from a PGN format string.
        Should be used only at the moment the object is created"""

        pgn = [i for i in pgn.split(" ") if "." not in i][:-1]
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

    def unconnect(self, n = "All"):
        if n == "All":
            for i in range(len(self.connections)):
                self.unconnect(i)
        else :
            if self.connections[n] != None:
                self.connections[n].send("!close")
                self.connections[n].close()

    def delete(self):
        self.unconnect()
        del self

class Connection:

    def __init__(self, host, address, port, debug = False):
        
        self.alive = True
        self.host, self.address, self.port  = host, address, port
        self.last_message = ""
        self.connected = False
        self.debug = debug
        threading.Thread(target = self.connect, daemon=True).start()
    
    def connect(self):
        if self.host:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setblocking(0)
            self.server.bind(("0.0.0.0", self.port))
            self.server.listen()
            address = None
            while self.address != address and self.alive:
                try :
                    self.conn, (address, _) = self.server.accept()
                    if address != self.address:
                        self.conn.close()
                        self.conn = None
                    else :
                        if self.debug:
                            print(f"Connected with {address}")
                            print("----------------")
                        break
                except BlockingIOError:
                    time.sleep(0.5)
                except OSError:
                    pass
            self.server.close()
        else :
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            redo = True
            while redo and self.alive:
                try :
                    redo = False
                    self.conn.connect((self.address, self.port))
                    if self.debug:
                        print(f"Connected with {self.address}")
                        print("----------------")
                except ConnectionRefusedError:
                    redo = True
                    time.sleep(0.5)
                except OSError:
                    pass
        
        if self.alive:
            self.conn.setblocking(1)
            self.connected = True
            threading.Thread(target=self.listening, daemon=True).start()

    def listening(self):
        while self.alive:
            try :
                self.last_message = self.conn.recv(1024).decode("utf-8")
                if self.last_message == "":
                    raise Exception()
                if self.debug:
                    print(f"[CONNECTION] >> {self.last_message}")
            except :
                if self.debug:
                    print("----------------")
                    print("Connection Lost")
                self.connected = False
                break

            if self.last_message == "!close":
                self.close()
                return

        if self.alive:
            self.connect()

    def send(self, message):
        if self.connected:
            try :
                self.conn.send(message.encode("utf-8"))
                if self.debug:
                    print(f"[CONNECTION] << {message}")
            except ConnectionResetError:
                if self.debug:
                    print(f"[DEBUG] error sending message {message}")
            except OSError:
                if self.debug:
                    print(f"[DEBUG] error sending message {message}")

    def close(self):
        
        self.alive = False
        self.connected = False

        if hasattr(self, "conn"):
            if self.conn != None:
                self.conn.close()

        if hasattr(self, "server"):
            if self.server != None:
                self.server.close()
        
        if self.debug:
            print("[DEBUG] connection closed cleanly")

        del self

    def end_connection(self, message = "!close"):
        last = 0
        while self.connected:
            if time.time() - last > 5:
                self.send(message)
                last = time.time()
            time.sleep(0.5)
        self.close()

class Button:

    def __init__(self, parent, text, pos, action, background_color = (40, 40, 40), text_color = (255, 255, 255)):
        self.parent = parent
        self.text = text
        self.size = pos[2:]
        self.pos = pos
        self.action = action
        self.background_color = background_color
        self.text_color = text_color
        self.state = "UP"
        self.is_over = False

        surface = pygame.font.SysFont("FreeSans Gras", 300).render(self.text, True, self.text_color, self.background_color)
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
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.state = "DOWN"
                    elif event.type == pygame.MOUSEBUTTONUP:
                        if self.state == "DOWN":
                            self.state = "UP"
                            self.action(self.parent)
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
            surface = pygame.transform.smoothscale(surface, (int(surface.get_width()*92/100), int(surface.get_height()*92/100)))
            surf.blit(surface, (int(self.size[0]/2-surface.get_width()/2),int(self.size[1]/2-surface.get_height()/2)))
            surface = surf
        return surface

class MainWindow:

    def __init__(self, board_settings = None):

        if board_settings == None:
            self.board_settings = settings.user_settings()
        else :
            self.board_settings = board_settings
        self.board_settings["parent"] = self
        self.board_settings["pos"] = (4, (self.board_settings["bsz"]//16))

        self.board = DisplayBoard(**self.board_settings)

        self.components = []

        #Initialise the window
        pygame.init()
        pygame.display.set_caption("little-chess-game")
        pygame.display.set_icon(pygame.image.load("asset/pieces/cburnett/bN.png"))
        self.window_surface = pygame.display.set_mode((self.board.board_size+8, self.board.board_size+self.board.board_size//16+4))
        
        def open_settings(window):
            settings.settings_window(window)

        self.components.append(Button(self, "Settings", (self.board.pos[0]+self.board.board_size*3//4+2, 4, (self.board.board_size//4)-2, (self.board.board_size//16)-8), open_settings))
        
        def restart(window):
            #Fermeture des sockets pour éviter des bugs comme la connection avec une socket inutilisée
            window.board.delete()
            window.board = DisplayBoard(**window.board_settings)

        self.components.append(Button(self, "Restart", (self.board.pos[0], 4, (self.board.board_size//4)-2, (self.board.board_size//16)-8),restart))

        def import_pgn(window):
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

        self.components.append(Button(self, "Import", (self.board.pos[0]+self.board.board_size//4+2, 4, (self.board.board_size//4)-4, (self.board.board_size//16)-8), import_pgn))

        def export(window):
            window.board.export_pgn()

        self.components.append(Button(self, "Export", (self.board.pos[0]+self.board.board_size*2//4+2, 4, (self.board.board_size//4)-4, (self.board.board_size//16)-8), export))
        
    def run(self, fps = 60):

        self.running = True
        clock = pygame.time.Clock()
        self.skip = False

        def render(element):
            self.window_surface.blit(element.handle_events(new_events), element.pos)

        while self.running :
            pygame.display.flip()
            clock.tick(fps)
            self.window_surface.fill((10, 10, 10))
            new_events = pygame.event.get()
            if not new_events:
                new_events.append(pygame.event.Event(0))
            for event in new_events:
                if event.type == pygame.QUIT:
                    self.running = False

            if not self.running:
                break

            render(self.board)
            for i in self.components:
                render(i)

if __name__ == "__main__":
    MainWindow().run()