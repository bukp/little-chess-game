import tkinter as tk
import pygame
import random
import chess

dark_color, light_color = (181, 136, 99), (240, 217, 181)
sprites = {i : pygame.transform.scale(pygame.image.load("asset/"+("b" if i.islower() else "w") +i.upper()+".png"), (60, 60)) for i in ["K", "P", "N", "B", "R", "Q", "k", "p", "n", "b", "r", "q"]}

def pos_to_coord(tup):
    """Transforme une position en pixel (celle de la souris) en ligne/colonne"""
    if board_side == "white":
        return (7-int(tup[1]/(board_size//8)), int(tup[0]/(board_size//8)))
    elif board_side == "black" :
        return (int(tup[1]/(board_size//8)), 7-int(tup[0]/(board_size//8)))

def coord_to_pos(tup):
    """Transforme des coordonnées en  ligne/colonne en pixel"""
    if board_side == "white":
        return ((board_size//8)*tup[1], (board_size//8)*7-(board_size//8)*tup[0])
    elif board_side == "black" :
        return ((board_size//8)*7-(board_size//8)*tup[1], (board_size//8)*tup[0])

def draw_board(board : chess.Board, held_piece : tuple, held_piece_moves : list, mouse_pos : tuple):
    """Dessine le plateau"""
    for row in range(8):
        for col in range(8):
            color = dark_color
            if (row+col)%2 == 1 : # Coloration blanc/noir (couleurs tirées de lichess)
                color = light_color
            if held_piece != None and held_piece == (row, col): 
                color = (color[0] - 75, color[1] - 50, color[2] + 30)
            if board.last_move != None and (row, col) in board.last_move:
                color = (color[0] - 70, color[1] - 20, color[2] - 70)
            
            pygame.draw.rect(window_surface, color, pygame.Rect(*coord_to_pos((row, col)), board_size//8, board_size//8)) #Dessine la case

            #Dessine les effets quand une pièce est tenue
            if (row, col) in held_piece_moves :
                color = (color[0] - 75, color[1] - 50, color[2] + 30)
                if pos_to_coord(mouse_pos) == (row, col):
                    pygame.draw.rect(window_surface, color, pygame.Rect(*coord_to_pos((row, col)), board_size//8, board_size//8)) # Dessine un rectangle plein sous la pièce si celle-ci peut se rendre sur la case
                else :
                    if board[row, col] != None:  # Dessine un cercle là ou la pièce peut se rendre (plein si case vide, sinon vide pour permettre de voir la pièce)
                        pygame.draw.circle(window_surface, color, (coord_to_pos((row, col))[0]+board_size//16, coord_to_pos((row, col))[1]+board_size//16), board_size//16, board_size//96)
                    else :
                        pygame.draw.circle(window_surface, color, (coord_to_pos((row, col))[0]+board_size//16, coord_to_pos((row, col))[1]+board_size//16), board_size//48)

            if (row, col) != held_piece and board[row, col] != None:  #Dessine la pièce sauf si celle-ci est actuellement tenue (sprite tirés de lichess)
                window_surface.blit(sprites[board[row, col].letter.lower() if board[row, col].color == 1 else board[row, col].letter], coord_to_pos((row, col)))

    if held_piece != None: #Si une pièce est tenue, la dessiner au bout de la souris
        window_surface.blit(sprites[board[held_piece].letter.lower() if board[held_piece].color == 1 else board[held_piece].letter], (mouse_pos[0] - board_size//16, mouse_pos[1] - board_size//16))

def promotion_choice(color, mouse_pos):
    """Dessine la fenêtre de choix pour la promotion"""
    pygame.draw.rect(window_surface, (255, 255, 255), pygame.Rect(0, 0, board_size//4, board_size//4))
    mouse_pos = (7-int(mouse_pos[1]/(board_size//8)), int(mouse_pos[0]/(board_size//8)))
    if mouse_pos[1] <= 1 and mouse_pos[0] >= 6 :
        pygame.draw.rect(window_surface, (175, 175, 175), pygame.Rect((board_size//8)*mouse_pos[1], ((board_size//8)*7)-(board_size//8)*mouse_pos[0], (board_size//8), (board_size//8)))
    d = {"Q" : (0, 0), "R" : ((board_size//8), 0), "B" : (0, (board_size//8)), "N" : ((board_size//8), (board_size//8))}
    for i in d:
        window_surface.blit(sprites[i.lower() if color == 1 else i], d[i])

def draw_popup(text):
    """Dessine la popup de fin de partie"""
    grey_surface = pygame.Surface((board_size, board_size))
    grey_surface.fill((50, 50, 50))
    grey_surface.set_alpha(125)
    window_surface.blit(grey_surface, (0, 0))
    cell_size = board_size//8
    pygame.draw.rect(window_surface, (255, 255, 255), pygame.Rect(cell_size*2, cell_size*3, cell_size*4, cell_size*2))
    pygame.draw.rect(window_surface, (0, 0, 0), pygame.Rect(cell_size*2, cell_size*3, cell_size*4, cell_size*2), max(1, int(3*board_size/480)))
    text1 = pygame.font.SysFont("FreeSans Gras", 35).render(text[0], True, (0, 0, 0), (255, 255, 255))
    if text1.get_width() > 220:
        text1 = pygame.font.SysFont("FreeSans Gras", 25).render(text[0], True, (0, 0, 0), (255, 255, 255))
    text2 = pygame.font.SysFont("FreeSans Gras", 50).render(text[1], True, (0, 0, 0), (255, 255, 255))
    text1 = pygame.transform.scale(text1, (int(text1.get_width()*board_size/480), int(text1.get_height()*board_size/480)))
    text2 = pygame.transform.scale(text2, (int(text2.get_width()*board_size/480), int(text2.get_height()*board_size/480)))
    text = pygame.Surface((max(text1.get_width(), text2.get_width()), text1.get_height() + text2.get_height()))
    text.fill((255, 255, 255))
    text.blit(text1, (text.get_width()/2 - text1.get_width()/2,0))
    text.blit(text2, (text.get_width()/2 - text2.get_width()/2,text1.get_height()))
    window_surface.blit(text, (board_size//2-text.get_width()/2, board_size//2-text.get_height()/2))

def start_a_game(settings = ("player", "bot"), bsd = "white", bsz = 480, board = None):
    global board_side
    global board_size
    board_side = bsd
    board_size = (bsz//8)*8

    #Charge les sprites des pièces
    global sprites
    for i in sprites:
        sprites[i] = pygame.transform.scale(sprites[i], (board_size//8, board_size//8))

    #Créée la fenêtre
    pygame.init()
    pygame.display.set_caption("Chess game")
    pygame.display.set_icon(pygame.image.load("asset/wN.png"))
    global window_surface
    window_surface = pygame.display.set_mode((board_size, board_size))

    #Création des variables
    running = True
    clock = pygame.time.Clock()
    mouse_pos = (0, 0)
    held_piece = None
    held_piece_moves = []

    #Initialisation du plateau
    if board == None :
        board = chess.Board()
    else :
        board = chess.board_from_fen(board)

    while running :
        clock.tick(60) #Limite à 60 FPS
        pygame.display.flip()
        draw_board(board, held_piece, held_piece_moves, mouse_pos)

        if board.get_state() != "Running" : #Si la partie est terminée
            draw_board(board, held_piece, held_piece_moves, mouse_pos)
            draw_popup(board.get_state())
            pygame.display.flip()
            while running:
                for event in pygame.event.get(): #Attend que l'utilisateur clique pour fermer la fenêtre
                    if event.type == pygame.QUIT or event.type == pygame.MOUSEBUTTONDOWN:
                        running = False

        elif running :
            if settings[board.turn] == "player": #Vérifie si le tour est à un joueur
                for event in pygame.event.get():

                    if event.type == pygame.QUIT:
                        running = False

                    if board.get_state() == "Running" :

                        if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION]: #Récupère la position de la souris
                            mouse_pos = event.pos

                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: #Récupère le clic gauche et met la pièce dans la main si il y en a une à l'endroit du clic
                            pos = pos_to_coord(event.pos)
                            if board[pos] != None and board[pos].color == board.turn:
                                held_piece = pos
                                held_piece_moves = []
                                lis = board.get_moves_starting_with(held_piece)
                                for i in lis:
                                    if i[1] not in lis:
                                        held_piece_moves.append(i[1])

                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3: #Repose la pièce si un clic droit est effectué
                            held_piece = None
                            held_piece_moves = []

                        if event.type == pygame.MOUSEBUTTONUP and event.button == 1: #Récupère l'arret de l'appuie sur le clic gauche et essaie de bouger la pièce à l'endroit déposé
                            moves, lis = board.get_moves_starting_with(held_piece), [] #Récupère tout les mouvements possibles 
                            for i in moves: #Ajoute les mouvements à lis si ceux-ci finissent sur la case ou la pièce a été lachée
                                lis.append(i[1])

                            choices = []
                            if pos_to_coord(event.pos) in lis:
                                for i in moves:
                                    if (i[0], i[1]) == (held_piece, pos_to_coord(event.pos)):
                                        choices.append(i)

                                if len(choices) > 1:  #Cas ou plusieurs coups légaux commencent et finissent par la même position (cas de la promotion)
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
                                                mouse_pos = event.pos #Récupère la position de la souris

                                            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                                                move_to_play = "Cancel" #Va annuler la promotion

                                            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                                                mouse_coord = (7-int(event.pos[1]/(board_size//8)), int(event.pos[0]/(board_size//8)))
                                                if mouse_coord[1] <= 1 and mouse_coord[0] >= 6:
                                                    move_to_play = choices[mouse_coord[0]*2-mouse_coord[1]-11] #Transforme la position du clic en l'indice du coup à jouer
                                                else :
                                                    move_to_play = "Cancel" #Va annuler la promotion
                                else :
                                    move_to_play = choices[0] #Si il n'y a qu'une possibilité, choisir cette possibilitée (99% des cas)
                                if move_to_play != "Cancel":
                                    board = board.move(move_to_play)
                            held_piece = None
                            held_piece_moves = []

            elif settings[board.turn] == "bot": #Vérifie si le tour est à un bot
                if board.get_state() == "Running":
                    draw_board(board, None, [], mouse_pos)
                    pygame.display.flip()
                    board = board.move(board.choose_best_move(1)) #Joue le coup
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False

            elif settings[board.turn] == "random": #Vérifie si le tour est à jouer aléatoirement
                if board.get_state() == "Running":
                    board = board.move(random.choice(board.get_all_possible_moves())) #Joue le coup
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False

if __name__ == "__main__":

    #Création de la fenêtre tkinter permettant le paramétrage de la partie
    
    size = (500, 110)
    window = tk.Tk()
    window.title("Game settings")
    window.geometry(f"{size[0]}x{size[1]}")
    window.resizable(False, False)
    window.iconphoto(True, tk.PhotoImage(file = "asset\\wN.png"))

    paned_window = tk.PanedWindow(window, orient=tk.HORIZONTAL)
    paned_window.pack(fill = tk.BOTH, pady=2, padx=2)

    frame1 = tk.LabelFrame(paned_window, text = "White player")
    paned_window.add(frame1)

    frame2 = tk.LabelFrame(paned_window, text = "Black player")
    paned_window.add(frame2)

    frame3 = tk.LabelFrame(paned_window, text = "View")
    paned_window.add(frame3)

    frame4 = tk.Frame(paned_window, padx = 5, pady = 5)
    paned_window.add(frame4)

    frame5 = tk.PanedWindow(window, orient = tk.HORIZONTAL)
    frame5.pack(fill = tk.BOTH, pady=2, padx=2)

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
        arg = ((liste1.get(liste1.curselection()[0]),liste2.get(liste2.curselection()[0])), liste3.get(liste3.curselection()[0]), int(size_set.get()), fen_entry.get())
        window.destroy()
        start_a_game(*arg)

    tk.Button(frame4, text="Create", command = create, width= 30).pack(expand = tk.Y)

    frame5.add(tk.Label(text = "Fen : "))

    fen_entry = tk.Entry(width = 60, )
    frame5.add(fen_entry)
    fen_entry.insert(0, "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
    

    window.mainloop()