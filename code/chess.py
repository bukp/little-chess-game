def int_to_name(row : int, col : int) -> tuple:
    """Convertit une position ligne/colonne en notation algébrique"""

    if 0 <= row <= 7 and 0 <= col <= 7:
        return chr(col + 97) + str(row+1)
    else : #n'arrive jamais en théorie
        raise Exception("Invalid input", row, col)

def name_to_int(key : str) -> tuple:
    """Convertit une notation algébrique en position ligne/colonne"""

    if 97 <= ord(key[0]) <= 104 and 1 <= int(key[1]) <= 8:
        return (int(key[1])-1, ord(key[0])-97)
    else : #n'arrive jamais en théorie
        raise Exception("Invalid input", key)

def grid_from_fen(fen : str) -> list:
    """Crée une grille contenant des pièces en fontion d'une chaine de caractère de format FEN"""

    out = [[None for _ in range(8)]for _ in range(8)]
    current = (7, 0)
    for i in fen:
        if i == "/":
            current = (current[0]-1, 0)
        elif i.isdigit():
            current = (current[0], current[1]+int(i))
        elif i.upper() == "P":
            out[current[0]][current[1]] = pawn(1 if i.islower() else 0)
            current = (current[0], current[1]+1)
        elif i.upper() == "N":
            out[current[0]][current[1]] = knight(1 if i.islower() else 0)
            current = (current[0], current[1]+1)
        elif i.upper() == "B":
            out[current[0]][current[1]] = bishop(1 if i.islower() else 0)
            current = (current[0], current[1]+1)
        elif i.upper() == "R":
            out[current[0]][current[1]] = rook(1 if i.islower() else 0)
            current = (current[0], current[1]+1)
        elif i.upper() == "Q":
            out[current[0]][current[1]] = queen(1 if i.islower() else 0)
            current = (current[0], current[1]+1)
        elif i.upper() == "K":
            out[current[0]][current[1]] = king(1 if i.islower() else 0)
            current = (current[0], current[1]+1)
    return out

def board_from_fen(fen : str) -> list:
    """Similaire à grid_from_fen mais renvoie un objet Board"""
    return Board(grid_from_fen(fen))

class Piece:
    """Objet représentant les pièces"""

    def __init__(self, list_moves, letter : str, name : str, color : int) -> None:
        self.list_moves = list_moves
        self.letter = letter
        self.name = name
        self.color = color

    def get_color(self) -> str:
        if self.color == 0: 
            return "white"
        else :
            return "black"
    
    def get_letter(self) -> str:
        return self.letter
    
    def __repr__(self) -> str:
        return f"{self.name}, color : {self.get_color()} "
    
    def copy(self):
        out = Piece(self.list_moves, self.letter, self.name, self.color)
        if hasattr(self, "can_castle"):
            out.__setattr__("can_castle", self.can_castle)
        return out

def king(color : int, can_castle : bool = True) -> Piece:
    """Fonction créant un objet pièce représentant le Roi"""

    def list_moves(piece_pos : tuple, board : Board, try_castle : bool = True) -> list:
        """Fonction calculant les différents mouvements possibles pour le Roi.
        Cette fontion est ajoutée en tant qu'attribut à la pièce créée"""
        
        possible_moves = []        
        for i in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]: #Liste des cases sur lesquelles le pièce peut aller
            if 0 <= i[0] + piece_pos[0] <= 7 and 0 <= i[1] + piece_pos[1] <= 7: #Vérifie si la case est sur le plateau
                possible_moves.append(((piece_pos[0], piece_pos[1]),(i[0] + piece_pos[0], i[1] + piece_pos[1])))
        
        to_remove = []
        for i in possible_moves: #Enlève les coups qui mangent des pièces alliées 
            if board[i[1]] != None and board[i[1]].color == board.grid[piece_pos[0]][piece_pos[1]].color: #enlève les coups qui mangent une pièce de la même couleur
                to_remove.append(i)
        for i in to_remove:
            possible_moves.remove(i)
        
        if try_castle == True:
            row = color * 7
            #Petit roque
            if board[row, 4] != None and board[row, 4].name == "King" and board[row, 4].can_castle == True:
                if board[row, 7] != None and board[row, 7].name == "Rook" and board[row, 7].can_castle == True:
                    if board[row, 5] == board[row, 6] == None:
                        if board.is_in_check(color, (row, 4)) == board.is_in_check(color, (row, 5)) == board.is_in_check(color, (row, 6)) == False :
                            possible_moves.append(((color * 7, 4), (color * 7, 6)))
            #Grand roque
            if board[row, 4] != None and board[row, 4].name == "King" and board[row, 4].can_castle == True:
                if board[row, 0] != None and board[row, 0].name == "Rook" and board[row, 0].can_castle == True:
                    if board[row, 3] == board[row, 2] == board[row, 1] == None:
                        if board.is_in_check(color, (row, 4)) == board.is_in_check(color, (row, 3)) == board.is_in_check(color, (row, 2)) == False :
                            possible_moves.append(((color * 7, 4), (color * 7, 2)))
        return possible_moves 
    
    result = Piece(list_moves, "K", "King", color)
    result.__setattr__("can_castle", can_castle)
    return result

def pawn(color : int) -> Piece:
    """Fonction créant un objet pièce représentant le Pion"""
    
    def list_moves(piece_pos : tuple, board : Board) -> list:
        """Fonction calculant les différents mouvements possibles pour le Pion.
        Cette fontion est ajoutée en tant qu'attribut à la pièce créée"""
        
        possible_moves = []
        color = board[piece_pos].color

        if True:
            if piece_pos[0] == 1 + color * 5: #Mouvement de 2 cases en avant pour le premier coup du pion
                if board[piece_pos[0]+1-2*color, piece_pos[1]] == board[piece_pos[0]+2-4*color, piece_pos[1]] == None:
                    possible_moves.append(((piece_pos[0], piece_pos[1]),(piece_pos[0]+2-4*color, piece_pos[1])))
            
            if board[piece_pos[0]+1-2*color, piece_pos[1]] == None : #Mouvement basique de 1 case en avant
                possible_moves.append(((piece_pos[0], piece_pos[1]),(piece_pos[0]+1-2*color, piece_pos[1])))

            if piece_pos[1]+1 <= 7 and board[piece_pos[0]+1-2*color, piece_pos[1]+1] != None:
                possible_moves.append(((piece_pos[0], piece_pos[1]),(piece_pos[0]+1-2*color, piece_pos[1]+1))) #Prise en diagonale vers la droite

            if piece_pos[1]-1 >= 0 and board[piece_pos[0]+1-2*color, piece_pos[1]-1] != None:
                possible_moves.append(((piece_pos[0], piece_pos[1]),(piece_pos[0]+1-2*color, piece_pos[1]-1))) #Prise en diagonale vers la gauche

            if board.last_move != None and board.last_move[1] == (piece_pos[0], piece_pos[1]+1) and board.last_move[0] == (piece_pos[0]+2-4*color, piece_pos[1]+1) and board[board.last_move[1]].name == "Pawn":
                possible_moves.append(((piece_pos[0], piece_pos[1]),(piece_pos[0]+1-2*color, piece_pos[1]+1), "&"+str(piece_pos[0])+str(piece_pos[1]+1))) #Prise en passant vers la droite
            
            if board.last_move != None and board.last_move[1] == (piece_pos[0], piece_pos[1]-1) and board.last_move[0] == (piece_pos[0]+2-4*color, piece_pos[1]-1) and board[board.last_move[1]].name == "Pawn":
                possible_moves.append(((piece_pos[0], piece_pos[1]),(piece_pos[0]+1-2*color, piece_pos[1]-1), "&"+str(piece_pos[0])+str(piece_pos[1]-1))) #Prise en passant vers la gauche

        to_remove = []
        for i in possible_moves: #Enlève les coups qui mangent des pièces alliées 
            if board[i[1]] != None and board[i[1]].color == board.grid[piece_pos[0]][piece_pos[1]].color: #enlève les coups qui mangent une pièce de la même couleur
                to_remove.append(i)
        for i in to_remove:
            possible_moves.remove(i)
        
        to_remove, to_add= [], []
        for i in possible_moves: #Ajoute la promotion pour les pions sur la dernière ou première rangée
            if i[1][0] == 0 or i[1][0] == 7:
                to_remove.append(i)
                for j in ["K", "B", "R", "Q"]:
                    to_add.append(i+("="+j,))
        for i in to_remove:
            possible_moves.remove(i)
        possible_moves += to_add

        return possible_moves 
    
    result = Piece(list_moves, "P", "Pawn", color)
    return result

def knight(color : int) -> Piece:
    """Fonction créant un objet pièce représentant le Cavalier"""
    
    def list_moves(piece_pos : tuple, board : Board) -> list:
        """Fonction calculant les différents mouvements possibles pour le Cavalier.
        Cette fontion est ajoutée en tant qu'attribut à la pièce créée"""
        
        possible_moves = []        
        for i in [(2, 1), (1, 2), (-2, 1), (-1, 2), (2, -1), (1, -2), (-2, -1), (-1, -2)]: #Liste des cases sur lesquelles le pièce peut aller
            if 0 <= i[0] + piece_pos[0] <= 7 and 0 <= i[1] + piece_pos[1] <= 7: #Vérifie si la case est sur le plateau
                possible_moves.append(((piece_pos[0], piece_pos[1]),(i[0] + piece_pos[0], i[1] + piece_pos[1])))
        
        to_remove = []
        for i in possible_moves: #Enlève les coups qui mangent des pièces alliées 
            if board[i[1]] != None and board[i[1]].color == board.grid[piece_pos[0]][piece_pos[1]].color: #enlève les coups qui mangent une pièce de la même couleur
                to_remove.append(i)
        for i in to_remove:
            possible_moves.remove(i)
        
        return possible_moves 

    result = Piece(list_moves, "N", "Knight", color)
    return result

def bishop(color : int) -> Piece:
    """Fonction créant un objet pièce représentant le Fou"""
    
    def list_moves(piece_pos : tuple, board : Board) -> list:
        """Fonction calculant les différents mouvements possibles pour le Fou.
        Cette fontion est ajoutée en tant qu'attribut à la pièce créée"""

        possible_moves = []
        for i in [(1, 1), (1, -1), (-1, 1), (-1, -1)]: #Liste des directions possibles pour la Pièce
            current = piece_pos
            #Regarde dans chaque direction et ajoute les cases tant qu'il n'est pas arrivé sur le bord du plateau ou sur une pièce
            while board.grid[current[0]][current[1]] == None or current == piece_pos : 
                current = (current[0] + i[0], current[1] + i[1])
                if current[0] < 0 or current[0] > 7 or current[1] < 0 or current[1] > 7: #Vérifie que la case est sur le plateau
                    break
                else :
                    possible_moves.append(((piece_pos[0], piece_pos[1]),current))
        
        to_remove = []
        for i in possible_moves: #Enlève les coups qui mangent des pièces alliées 
            if board[i[1]] != None and board[i[1]].color == board.grid[piece_pos[0]][piece_pos[1]].color: #enlève les coups qui mangent une pièce de la même couleur
                to_remove.append(i)
        for i in to_remove:
            possible_moves.remove(i)
        
        return possible_moves 
    
    result = Piece(list_moves, "B", "Bishop", color)
    return result

def rook(color : int, can_castle : bool = True) -> Piece:
    """Fonction créant un objet pièce représentant la Tour"""
    
    def list_moves(piece_pos : tuple, board : Board) -> list:
        """Fonction calculant les différents mouvements possibles pour la Tour.
        Cette fontion est ajoutée en tant qu'attribut à la pièce créée"""

        possible_moves = []
        for i in [(0, 1), (0, -1), (1, 0), (-1, 0)]: #Liste des directions possibles pour la Pièce
            current = piece_pos
            #Regarde dans chaque direction et ajoute les cases tant qu'il n'est pas arrivé sur le bord du plateau ou sur une pièce
            while board.grid[current[0]][current[1]] == None or current == piece_pos : 
                current = (current[0] + i[0], current[1] + i[1])
                if current[0] < 0 or current[0] > 7 or current[1] < 0 or current[1] > 7: #Vérifie que la case est sur le plateau
                    break
                else :
                    possible_moves.append(((piece_pos[0], piece_pos[1]),current))
        
        to_remove = []
        for i in possible_moves: #Enlève les coups qui mangent des pièces alliées 
            if board[i[1]] != None and board[i[1]].color == board.grid[piece_pos[0]][piece_pos[1]].color: #enlève les coups qui mangent une pièce de la même couleur
                to_remove.append(i)
        for i in to_remove:
            possible_moves.remove(i)
        
        return possible_moves 

    result = Piece(list_moves, "R", "Rook", color)
    result.__setattr__("can_castle", can_castle)
    return result

def queen(color : int) -> Piece:
    """Fonction créant un objet pièce représentant la Dame"""
    
    def list_moves(piece_pos : tuple, board : Board) -> list:
        """Fonction calculant les différents mouvements possibles pour la Dame.
        Cette fontion est ajoutée en tant qu'attribut à la pièce créée"""

        possible_moves = []
        for i in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]: #Liste des directions possibles pour la Pièce
            current = piece_pos
            #Regarde dans chaque direction et ajoute les cases tant qu'il n'est pas arrivé sur le bord du plateau ou sur une pièce
            while board.grid[current[0]][current[1]] == None or current == piece_pos : 
                current = (current[0] + i[0], current[1] + i[1])
                if current[0] < 0 or current[0] > 7 or current[1] < 0 or current[1] > 7: #Vérifie que la case est sur le plateau 
                    break
                else :
                    possible_moves.append(((piece_pos[0], piece_pos[1]),current))
        
        to_remove = []
        for i in possible_moves: #Enlève les coups qui mangent des pièces alliées 
            if board[i[1]] != None and board[i[1]].color == board.grid[piece_pos[0]][piece_pos[1]].color: #enlève les coups qui mangent une pièce de la même couleur
                to_remove.append(i)
        for i in to_remove:
            possible_moves.remove(i)
        
        return possible_moves 

    result = Piece(list_moves, "Q", "Queen", color)
    return result

class Board:
    """Objet représentant le plateau.
    Il n'est pas destiné à changer pendant l'execution"""

    def __init__(self, grid : list = "start", turn : int = 0, last_move : str = None, fen_list = [], last_capture = 0) -> None:
        self.turn = turn
        if grid == "start":
            self.grid = grid_from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR") #Position de départ en format FEN
        elif grid == "empty":
            self.grid = [[None for _ in range(8)]for _ in range(8)] #Grille vide
        else :
            if type(grid) == str:
                self.grid = grid_from_fen(grid) #Si l'argument grid est une chaine de caractère on transforme la chaine de caractère en grille avec grid_from_fen
            else:
                self.grid = grid
        self.last_move = last_move
        self.fen_list = fen_list
        self.last_capture = last_capture

    def __getitem__(self, key : tuple) -> Piece:
        """Renvoie la pièce présente à l'endroit demandé, renvoie None si qucune pièce n'est présente.
        Cette fonction est appelée avec Board[key]"""

        if type(key) == str: #n'arrive jamais en théorie
            key = name_to_int(key)
            print("Debug : An item as been getted with str key", self.grid[key[0]][key[1]])
        return self.grid[key[0]][key[1]]

    def __setitem__(self, key : int, value) -> None:
        """Définie la valeur d'une case du plateau.
        Cette fonction est appelée avec Board[key] = value"""
        
        if type(key) == str: #n'arrive jamais en théorie
            key = name_to_int(key)
            print("Debug : An item as been setted with str key", self.grid[key[0]][key[1]])
        self.grid[key[0]][key[1]] = value

    def __repr__(self) -> str:
        """Renvoie un string représentant le plateau.
        Cette fonction est appelée avec print(Board) ou str(Board)"""

        r = ""
        for row in range(7, -1, -1):
            r += "\n"
            for col in range(8):
                r += "  "
                if self[row,col] == None :
                    r += "."
                else : 
                    if self[row,col].color == 0:
                        r += self[row,col].get_letter()
                    else :
                        r += self[row,col].get_letter().lower()
        return r

    def copy_grid(self) -> list:
        """Retourne une copie de la grille dont les éléments sont distincts de la grille originale (on peut la modifier sans modifier l'originale)"""
        return [[self[row,col].copy() if self[row,col] != None else None for col in range(8)]for row in range(8)]

    def to_fen(self) -> str:
        """Renvoie une chaine au format FEN représentant le plateau"""

        out = ""
        for row in range(7, -1, -1):
            for col in range(8):
                if self[row, col] == None:
                    if len(out) > 0 and out[-1].isdigit():
                        out = out[:-1] + str(int(out[-1])+1)
                    else :
                        out += "1"
                else :
                    if self[row, col].color == 0:
                        out += self[row, col].letter
                    else :
                        out += self[row, col].letter.lower()
            out += "/"
        return out[:-1]

    def move(self, movement : tuple):
        """Renvoie un objet Board auquel on a bougé une pièce le mouvement est un tuple de deux tuple désignant la position de départ et la position d'arrivée"""

        new_board = Board(self.copy_grid(), (self.turn + 1)%2, movement, self.fen_list + [self.to_fen()], 0 if type(movement) == tuple and (self[movement[1]] != None or self[movement[0]].name == "Pawn") else self.last_capture + 1)

        if (movement == ((0, 4), (0, 6)) or movement == ((7, 4), (7, 6))) and self[movement[0]].name == "King" and self[movement[0]].can_castle: #Petit roque 
            new_board[self.turn * 7,6], new_board[self.turn * 7,4] = new_board[self.turn * 7,4], None
            new_board[self.turn * 7,5], new_board[self.turn * 7,7] = new_board[self.turn * 7,7], None
            new_board[self.turn * 7,6].can_castle, new_board[self.turn * 7,5].can_castle = False, False

        elif (movement == ((0, 4), (0, 2)) or movement == ((7, 4), (7, 2))) and self[movement[0]].name == "King" and self[movement[0]].can_castle: #Grand roque
            new_board[self.turn * 7,2], new_board[self.turn * 7,4] = new_board[self.turn * 7,4], None
            new_board[self.turn * 7,3], new_board[self.turn * 7,0] = new_board[self.turn * 7,0], None
            new_board[self.turn * 7,2].can_castle, new_board[self.turn * 7,3].can_castle = False, False
        else:

            start_pos, end_pos, arg = movement[0], movement[1], movement[2] if len(movement)>2 else None #Décompose le mouvement

            new_board[end_pos], new_board[start_pos] = new_board[start_pos], None
            if hasattr(new_board[end_pos], "can_castle"): #Si la pièce qui a bougé peut roquer, lui enlever le droit de roquer
                new_board[end_pos].can_castle = False

            if arg != None:
                if "=" in arg: #Détection de la promotion
                    if arg[1] == "K":
                        new_board[end_pos] = knight(new_board[end_pos].color)
                    if arg[1] == "B":
                        new_board[end_pos] = bishop(new_board[end_pos].color)
                    if arg[1] == "R":
                        new_board[end_pos] = rook(new_board[end_pos].color, can_castle = False)
                    if arg[1] == "Q":
                        new_board[end_pos] = queen(new_board[end_pos].color)

                elif "&" in arg: #Détection de la prise en passant
                    new_board[int(movement[2][1]),int(movement[2][2])] = None

        return new_board

    def is_in_check(self, color, pos : tuple = "king_pos") -> bool:
        if pos == "king_pos":
            for row in range(8):
                for col in range(8):
                    if self[row,col] != None and self[row,col].name == "King" and self[row,col].color == color: #Cherche le roi sur tout le plateau
                        pos = (row, col)
            if pos == "king_pos": #Cas ou le roi aurait disparu de l'échéquier (n'arrive jamais en théorie)
                raise Exception("The king is not foundable : "+ self.last_move)
        
        #Regarde tout les mouvements possibles et regarde si un mouvement fini à la position du Roi
        for i in self.get_all_possible_moves(False, False, (color+1)%2):
            if i[1] == pos:
                return True
        return False

    def get_state(self):
        """Renvoie l'état de la partie (Victoire, Défaite, Nulle, Pat, ...), renvoie "running" si la partie n'est pas terminée"""

        remaining_white_pieces = []
        remaining_black_pieces = []
        eval = "Running"
        for row in range(8):
            for col in range(8):
                if self[row, col] != None:
                    if self[row, col].color == 0:
                        remaining_white_pieces.append(self[row, col].letter)
                    else :
                        remaining_black_pieces.append(self[row, col].letter)
        
        white_is_in_material_deficiency = remaining_white_pieces.count("P") == remaining_white_pieces.count("Q") == remaining_white_pieces.count("R") == 0 and remaining_white_pieces.count("B") + remaining_white_pieces.count("N") <= 1
        black_is_in_material_deficiency = remaining_black_pieces.count("P") == remaining_black_pieces.count("Q") == remaining_black_pieces.count("R") == 0 and remaining_black_pieces.count("B") + remaining_black_pieces.count("N") <= 1

        if self.fen_list.count(self.to_fen()) >= 2:
            return ("Draw by repetition", "½ - ½")

        if self.last_capture >= 50:
            return ("Draw by the fifty-moves rule", "½ - ½")

        if white_is_in_material_deficiency and black_is_in_material_deficiency :
            return ("Draw by material deficiency", "½ - ½")
        
        if len(self.get_all_possible_moves()) == 0:
            if self.is_in_check(self.turn) :
                if self.turn == 0:
                    return ("Black won by Mat", "0 - 1")
                else :
                    return ("White won by Mat", "1 - 0")
            else :
                return ("Stalemate", "½ - ½")

        return eval

    def get_all_possible_moves(self, check_verif : bool = True , try_castle : bool = True, color = None, sort = False) -> list:
        """Renvoie une liste de touts les mouvements possibles dans cette position"""

        if color == None : color = self.turn
        out = []
        for row in range(8):
            for col in range(8):
                if self[row,col] != None and self[row,col].color == color:
                    for move in self[row,col].list_moves((row, col), self) if self[row,col].name != "King" else self[row,col].list_moves((row, col), self, try_castle):
                        if check_verif:
                            if not self.move(move).is_in_check(self.turn):
                                out.append(move)
                        else:
                            out.append(move)
        return out

    def get_moves_starting_with(self, start_pos):
        """Renvoie une liste des mouvement possibles pour une pièce donnée"""

        out = []
        for i in self.get_all_possible_moves():
            if i[0] == start_pos:
                out.append(i)
        return out

    def make_readeable(self, movement : tuple) -> str:
        """Renvoie un string de la notation algébrique abrégée du mouvement depuis ce plateau"""

        if type(movement) != tuple:
            return movement
        out = ""
        if self[movement[0]].name != "Pawn" :
            out += self[movement[0]].letter
        
        other_starting_points = []
        for i in self.get_all_possible_moves():
            if i[1] == movement[1] and self[i[0]].name == self[movement[0]].name and i[0] != movement[0]:
                other_starting_points.append(i[0])
        if len(other_starting_points) > 0 :
            if [i[1] for i in other_starting_points].count(movement[0][1]) == 0:
                out += int_to_name(*movement[0])[0]
            else :
                if [i[0] for i in other_starting_points].count(movement[0][0]) == 0:
                    out += int_to_name(*movement[0])[1]
                else :
                    out += int_to_name(*movement[0])
        
        if self[movement[1]] != None or len(movement) > 2 and "&" in movement[2] :
            if len(out) == 0 :
                out = int_to_name(*movement[0])[0]
            out += "x"

        out += int_to_name(*movement[1])
        if len(movement)>2 and "=" in movement[2]:
            out += movement[2]
        
        new_board = self.move(movement)
        if new_board.is_in_check(new_board.turn):
            if len(new_board.get_all_possible_moves()) == 0:
                out += "#"
            else :
                out += "+"
        return out

    def static_eval(self) -> int:
        """Attribut une note à un plateau en fonction de l'état de la partie (mat, pat, ...), de la valeur des pièces qui s'y trouvent et de la liberté de mouvement des pièces"""

        if len(self.get_all_possible_moves()) == 0:
            if self.is_in_check(self.turn) : #Echec et mat
                if self.turn == 0:
                    return float("-inf") 
                else :
                    return float("inf")
            else :
                return 0 #Pat

        if self.fen_list.count(self.to_fen()) >= 2: #Répétition
            return 0

        if self.last_capture >= 50: #règle des 50 coups
            return 0

        else :
            remaining_white_pieces = []
            remaining_black_pieces = []
            value = {"P" : 1, "K" : 5, "N" : 3, "B" : 3.5, "R" : 5, "Q" : 9,}
            eval = 0
            for row in range(8):
                for col in range(8):
                    if self[row, col] != None:
                        if self[row, col].color == 0:
                            eval += value[self[row, col].letter] #Valeur brute de la pièce
                            move_list = self[row, col].list_moves((row, col), self)
                            eval += len(move_list) / 30 #Liberté de mouvement
                            for i in move_list:
                                if self[i[1]] != None: #Bonus si la pièce attaque ou défend une pièce importante 
                                    if self[i[1]].color == 0:
                                        eval += value[self[i[1]].letter] / 10 
                                    else :
                                        eval += value[self[i[1]].letter] / 10
                            remaining_white_pieces.append(self[row, col].letter)
                        else :
                            eval -= value[self[row, col].letter] #Valeur brute de la pièce
                            move_list = self[row, col].list_moves((row, col), self)
                            eval -= len(move_list) / 30 #Liberté de mouvement
                            for i in move_list:
                                if self[i[1]] != None: #Bonus si la pièce attaque ou défend une pièce importante
                                    if self[i[1]].color == 1:
                                        eval -= value[self[i[1]].letter] / 10
                                    else :
                                        eval -= value[self[i[1]].letter] / 10
                            remaining_black_pieces.append(self[row, col].letter)
            
            white_is_in_material_deficiency = remaining_white_pieces.count("P") == remaining_white_pieces.count("Q") == remaining_white_pieces.count("R") == 0 and remaining_white_pieces.count("B") + remaining_white_pieces.count("N") <= 1
            black_is_in_material_deficiency = remaining_black_pieces.count("P") == remaining_black_pieces.count("Q") == remaining_black_pieces.count("R") == 0 and remaining_black_pieces.count("B") + remaining_black_pieces.count("N") <= 1

            if white_is_in_material_deficiency and black_is_in_material_deficiency : #Déficience métérielle
                return 0

        return round(eval, 1)

    def sorting_eval(self) -> int:
        """Evaluation statique très sommaire servant à trier les coups"""

        value = {"P" : 1, "K" : 10, "N" : 3, "B" : 3.5, "R" : 5, "Q" : 9,}
        eval = 0
            
        for row in range(8):
            for col in range(8):
                if self[row, col] != None:
                    if self[row, col].color == 0:
                        eval += value[self[row, col].letter]
                    else :
                        eval -= value[self[row, col].letter]
        return eval
            
    def recursive_eval(self, n, a, b) -> int:
        """Evaluation récursive avec l'algorithme alpha-beta """

        if n <= 0:
            return self.static_eval()
        else :
            if self.turn == 0:
                all_possible_moves = self.get_all_possible_moves()
                all_possible_moves.sort(key = lambda x : self.move(x).sorting_eval(),reverse = True)
                best_move = float("-inf")
                if len(all_possible_moves)<=0:
                    return self.static_eval()
                for i in all_possible_moves:
                    eval = self.move(i).recursive_eval(n-1, a, best_move)
                    best_move = max(best_move, eval)
                    if best_move > b: #Elagage alpha-beta
                        return best_move
            else :
                all_possible_moves = self.get_all_possible_moves()
                all_possible_moves.sort(key = lambda x : self.move(x).sorting_eval(),reverse = False)
                best_move = float("inf")
                if len(all_possible_moves)<=0:
                    return self.static_eval()
                for i in all_possible_moves:
                    eval = self.move(i).recursive_eval(n-1, best_move, b)
                    best_move = min(best_move, eval)
                    if best_move < a: #Elagage alpha-beta
                        return best_move
            return best_move

    def choose_best_move(self, n) -> tuple:
        """Renvoie le meilleur mouvement (sous forme de tuple) d'après l'évaluation récursive"""

        all_possible_moves = self.get_all_possible_moves()
        all_possible_moves.sort(key = lambda x : self.move(x).sorting_eval(),reverse = not self.turn)
        best_move = (all_possible_moves[0], self.move(all_possible_moves[0]).recursive_eval(n, float("-inf"), float("inf")))
        for j in all_possible_moves:
            if self.turn == 0 : 
                eval = self.move(j).recursive_eval(n, best_move[1], float("inf"))
                if eval > best_move[1]:
                    best_move = (j, eval)
            else :
                eval = self.move(j).recursive_eval(n, float("-inf"), best_move[1])
                if eval < best_move[1]:
                    best_move = (j, eval)
        return best_move[0]