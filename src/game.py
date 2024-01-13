import threading
import settings
import pygame
import random
import chess

DEFAULT_SETTINGS = {"settings": ["player", "bot"], "bsd": "white", "bsz": 480, "board": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR", "pieces_style": "cburnett", "board_style": "brown"}

class DisplayBoard():

    def __init__(self,parent, board, board_side, board_size, settings, sprites, pos = (0, 0)):
        self.parent = parent
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
        held_piece = self.temp_var["held_piece"] if "held_piece" in self.temp_var else None
        held_piece_moves = self.temp_var["held_piece_moves"] if "held_piece_moves" in self.temp_var else []
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
                        if self.board[row, col] != None:  # Draw circles where the piece can go (full if the square is empty, else empty to allow the user to see the piece)
                            pygame.draw.circle(cell_surface, color, (self.board_size//16, self.board_size//16), self.board_size//16, self.board_size//96)
                        else :
                            pygame.draw.circle(cell_surface, color, (self.board_size//16, self.board_size//16), self.board_size//48)
                    board_surface.blit(cell_surface, self.coord_to_pos((row, col)))
                
                elif self.board.last_move != None and (row, col) in self.board.last_move:
                    color = (0, 180, 0, 75)
                    cell_surface = pygame.Surface((self.board_size//8, self.board_size//8), pygame.SRCALPHA)
                    cell_surface.fill(color)
                    board_surface.blit(cell_surface, self.coord_to_pos((row, col)))

                if (row, col) != held_piece and self.board[row, col] != None:  # Draw the piece unless it's held (sprites taken from lichess)
                    board_surface.blit(self.sprites[self.board[row, col].letter.lower() if self.board[row, col].color == 1 else self.board[row, col].letter], self.coord_to_pos((row, col)))

        if held_piece != None: # If the piece is hels, draw it under the mouse
            board_surface.blit(self.sprites[self.board[held_piece].letter.lower() if self.board[held_piece].color == 1 else self.board[held_piece].letter], (mouse_pos[0] - self.board_size//16, mouse_pos[1] - self.board_size//16))
        return board_surface

    def promotion_choice(self, surface, mouse_pos):
        """Draw promotion window"""
        pygame.draw.rect(surface, (255, 255, 255), pygame.Rect(0, 0, self.board_size//4, self.board_size//4))
        mouse_pos = (7-int(mouse_pos[1]/(self.board_size//8)), int(mouse_pos[0]/(self.board_size//8)))
        if mouse_pos[1] <= 1 and mouse_pos[0] >= 6 :
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
                                mouse_coord = (7-int(self.mouse[1]/(self.board_size//8)), int(self.mouse[0]/(self.board_size//8)))
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

class Button():

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
            surface = pygame.transform.smoothscale(surface, (int(surface.get_width()*9/10), int(surface.get_height()*9/10)))
            surf.blit(surface, (int(self.size[0]/2-surface.get_width()/2),int(self.size[1]/2-surface.get_height()/2)))
            surface = surf
        return surface

def create_game(parent, settings = ("player", "bot"), bsd = "white", bsz = 480, board = "start", pieces_style = "cburnett", board_style = "brown", pos = (0, 0)):
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

    board = DisplayBoard(parent, chess.Board(board), board_side, board_size, settings, sprites, pos)
    return board

class MainWindow:

    def __init__(self, board_settings = None):
        if board_settings == None:
            self.board_settings = settings.user_settings()
        else :
            self.board_settings = board_settings
        self.board_settings["parent"] = self
        self.board_settings["pos"] = (4, (self.board_settings["bsz"]//16))

        self.board = create_game(**self.board_settings)

        #Initialise the window
        pygame.init()
        pygame.display.set_caption("little-chess-game")
        pygame.display.set_icon(pygame.image.load("asset/pieces/cburnett/bN.png"))
        self.window_surface = pygame.display.set_mode((self.board.board_size+8, self.board.board_size+self.board.board_size//16+4))
        
        self.components = []

        def restart(window):
            window.board = create_game(**window.board_settings)

        self.components.append(Button(self, "Restart", (self.board.pos[0], 4, (self.board.board_size//4)-2, (self.board.board_size//16)-8),restart))

        def open_settings(window):
            settings.settings_window(window)

        self.components.append(Button(self, "Settings", (self.board.pos[0]+self.board.board_size//4+2, 4, (self.board.board_size//4)-4, (self.board.board_size//16)-8),open_settings))

        def func1(window):
            pass

        self.components.append(Button(self, "", (self.board.pos[0]+self.board.board_size*2//4+2, 4, (self.board.board_size//4)-4, (self.board.board_size//16)-8), func1))
        
        def func2(window):
            pass

        self.components.append(Button(self, "", (self.board.pos[0]+self.board.board_size*3//4+2, 4, (self.board.board_size//4)-2, (self.board.board_size//16)-8), func2))

    def run(self, fps = 60):

        running = True
        clock = pygame.time.Clock()

        def render(element):
            self.window_surface.blit(element.handle_events(new_events), element.pos)

        while running :
            pygame.display.flip()
            clock.tick(fps)
            self.window_surface.fill((10, 10, 10))
            new_events = pygame.event.get()
            if not new_events:
                new_events.append(pygame.event.Event(0))
            for event in new_events:
                if event.type == pygame.QUIT:
                    running = False
            
            if running:
                render(self.board)
                for i in self.components:
                    render(i)

if __name__ == "__main__":
    MainWindow().run()