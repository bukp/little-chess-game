def int_to_name(row : int, col : int) -> tuple:
    """Converts row/column position to algebraic notation"""

    if 0 <= row <= 7 and 0 <= col <= 7:
        return chr(col + 97) + str(row+1)
    else : #not supposed to happen
        raise Exception("Invalid input", row, col)

def name_to_int(key : str) -> tuple:
    """Converts algebraic notation to row/column position"""

    if 97 <= ord(key[0]) <= 104 and 1 <= int(key[1]) <= 8:
        return (int(key[1])-1, ord(key[0])-97)
    else : #not supposed to happen
        raise Exception("Invalid input", key)

def grid_from_fen(fen : str) -> list:
    """Creates a grid containing parts based on a string in FEN format"""

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
    """Similar to grid_from_fen but returns a Board object"""
    return Board(grid_from_fen(fen))

class Piece:
    """Object standing for pieces"""

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
    """Function creating a piece object representing the King"""

    def list_moves(piece_pos : tuple, board : Board, try_castle : bool = True) -> list:
        """Function calculating all possible moves for the King.
        This function will be added as an attribut"""
        
        possible_moves = []        
        for i in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]: #List all the squares on which the piece can go
            if 0 <= i[0] + piece_pos[0] <= 7 and 0 <= i[1] + piece_pos[1] <= 7: #Check if that square is on the board
                possible_moves.append(((piece_pos[0], piece_pos[1]),(i[0] + piece_pos[0], i[1] + piece_pos[1])))
        
        to_remove = []
        for i in possible_moves:
            if board[i[1]] != None and board[i[1]].color == board.grid[piece_pos[0]][piece_pos[1]].color: #Get rid off the moves that attack allies
                to_remove.append(i)
        for i in to_remove:
            possible_moves.remove(i)
        
        if try_castle == True:
            row = color * 7
            #Short castle
            if board[row, 4] != None and board[row, 4].name == "King" and board[row, 4].can_castle == True:
                if board[row, 7] != None and board[row, 7].name == "Rook" and board[row, 7].can_castle == True:
                    if board[row, 5] == board[row, 6] == None:
                        if board.is_in_check(color, (row, 4)) == board.is_in_check(color, (row, 5)) == board.is_in_check(color, (row, 6)) == False :
                            possible_moves.append(((color * 7, 4), (color * 7, 6)))
            #Long castle
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
    """Function creating a piece object representing the pawn"""
    
    def list_moves(piece_pos : tuple, board : Board) -> list:
        """Function calculating all possible moves for the pawn.
        This function will be added as an attribut"""
        
        possible_moves = []
        color = board[piece_pos].color

        if True:
            if piece_pos[0] == 1 + color * 5: #Move 2 squares forward for the pawn's first move
                if board[piece_pos[0]+1-2*color, piece_pos[1]] == board[piece_pos[0]+2-4*color, piece_pos[1]] == None:
                    possible_moves.append(((piece_pos[0], piece_pos[1]),(piece_pos[0]+2-4*color, piece_pos[1])))
            
            if board[piece_pos[0]+1-2*color, piece_pos[1]] == None : #Move 1 square forward
                possible_moves.append(((piece_pos[0], piece_pos[1]),(piece_pos[0]+1-2*color, piece_pos[1])))

            if piece_pos[1]+1 <= 7 and board[piece_pos[0]+1-2*color, piece_pos[1]+1] != None:
                possible_moves.append(((piece_pos[0], piece_pos[1]),(piece_pos[0]+1-2*color, piece_pos[1]+1))) #Capture diagonally to the right

            if piece_pos[1]-1 >= 0 and board[piece_pos[0]+1-2*color, piece_pos[1]-1] != None:
                possible_moves.append(((piece_pos[0], piece_pos[1]),(piece_pos[0]+1-2*color, piece_pos[1]-1))) #Capture diagonally to the left

            if board.last_move != None and board.last_move[1] == (piece_pos[0], piece_pos[1]+1) and board.last_move[0] == (piece_pos[0]+2-4*color, piece_pos[1]+1) and board[board.last_move[1]].name == "Pawn":
                possible_moves.append(((piece_pos[0], piece_pos[1]),(piece_pos[0]+1-2*color, piece_pos[1]+1), "&"+str(piece_pos[0])+str(piece_pos[1]+1))) #En passant capture to the right
            
            if board.last_move != None and board.last_move[1] == (piece_pos[0], piece_pos[1]-1) and board.last_move[0] == (piece_pos[0]+2-4*color, piece_pos[1]-1) and board[board.last_move[1]].name == "Pawn":
                possible_moves.append(((piece_pos[0], piece_pos[1]),(piece_pos[0]+1-2*color, piece_pos[1]-1), "&"+str(piece_pos[0])+str(piece_pos[1]-1))) #En passant capture to the left

        to_remove = []
        for i in possible_moves:
            if board[i[1]] != None and board[i[1]].color == board.grid[piece_pos[0]][piece_pos[1]].color: #Get rid off the moves that attack allies
                to_remove.append(i)
        for i in to_remove:
            possible_moves.remove(i)
        
        to_remove, to_add= [], []
        for i in possible_moves: #Add promotion for first and last row
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
    """Function creating a piece object representing the Knight"""
    
    def list_moves(piece_pos : tuple, board : Board) -> list:
        """Function calculating all possible moves for the Knight.
        This function will be added as an attribut"""
        
        possible_moves = []        
        for i in [(2, 1), (1, 2), (-2, 1), (-1, 2), (2, -1), (1, -2), (-2, -1), (-1, -2)]: #List all the squares on which the piece can go
            if 0 <= i[0] + piece_pos[0] <= 7 and 0 <= i[1] + piece_pos[1] <= 7: #Check if that square is on the board
                possible_moves.append(((piece_pos[0], piece_pos[1]),(i[0] + piece_pos[0], i[1] + piece_pos[1])))
        
        to_remove = []
        for i in possible_moves:
            if board[i[1]] != None and board[i[1]].color == board.grid[piece_pos[0]][piece_pos[1]].color: #Get rid off the moves that attack allies
                to_remove.append(i)
        for i in to_remove:
            possible_moves.remove(i)
        
        return possible_moves 

    result = Piece(list_moves, "N", "Knight", color)
    return result

def bishop(color : int) -> Piece:
    """Function creating a piece object representing the Bishop"""
    
    def list_moves(piece_pos : tuple, board : Board) -> list:
        """Function calculating all possible moves for the Bishop.
        This function will be added as an attribut"""

        possible_moves = []
        for i in [(1, 1), (1, -1), (-1, 1), (-1, -1)]: #List all possible directions for the piece
            current = piece_pos
            #Look in each direction and add the squares until reaching the edge of the board or encountering a piece.
            while board.grid[current[0]][current[1]] == None or current == piece_pos : 
                current = (current[0] + i[0], current[1] + i[1])
                if current[0] < 0 or current[0] > 7 or current[1] < 0 or current[1] > 7: #Check if the square is on the board
                    break
                else :
                    possible_moves.append(((piece_pos[0], piece_pos[1]),current))
        
        to_remove = []
        for i in possible_moves:
            if board[i[1]] != None and board[i[1]].color == board.grid[piece_pos[0]][piece_pos[1]].color: #Get rid off the moves that attack allies
                to_remove.append(i)
        for i in to_remove:
            possible_moves.remove(i)
        
        return possible_moves 
    
    result = Piece(list_moves, "B", "Bishop", color)
    return result

def rook(color : int, can_castle : bool = True) -> Piece:
    """Function creating a piece object representing the Rook"""
    
    def list_moves(piece_pos : tuple, board : Board) -> list:
        """Function calculating all possible moves for the Rook.
        This function will be added as an attribut"""

        possible_moves = []
        for i in [(0, 1), (0, -1), (1, 0), (-1, 0)]: #List all possible directions for the piece
            current = piece_pos
            #Look in each direction and add the squares until reaching the edge of the board or encountering a piece
            while board.grid[current[0]][current[1]] == None or current == piece_pos : 
                current = (current[0] + i[0], current[1] + i[1])
                if current[0] < 0 or current[0] > 7 or current[1] < 0 or current[1] > 7: #Check if the square is on the board
                    break
                else :
                    possible_moves.append(((piece_pos[0], piece_pos[1]),current))
        
        to_remove = []
        for i in possible_moves:
            if board[i[1]] != None and board[i[1]].color == board.grid[piece_pos[0]][piece_pos[1]].color: #Get rid off the moves that attack allies
                to_remove.append(i)
        for i in to_remove:
            possible_moves.remove(i)
        
        return possible_moves 

    result = Piece(list_moves, "R", "Rook", color)
    result.__setattr__("can_castle", can_castle)
    return result

def queen(color : int) -> Piece:
    """Function creating a piece object representing the Queen"""
    
    def list_moves(piece_pos : tuple, board : Board) -> list:
        """Function calculating all possible moves for the Queen.
        This function will be added as an attribut"""

        possible_moves = []
        for i in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]: #List all possible directions for the piece
            current = piece_pos
            #Look in each direction and add the squares until reaching the edge of the board or encountering a piece
            while board.grid[current[0]][current[1]] == None or current == piece_pos : 
                current = (current[0] + i[0], current[1] + i[1])
                if current[0] < 0 or current[0] > 7 or current[1] < 0 or current[1] > 7: #Check if the square is on the board 
                    break
                else :
                    possible_moves.append(((piece_pos[0], piece_pos[1]),current))
        
        to_remove = []
        for i in possible_moves:
            if board[i[1]] != None and board[i[1]].color == board.grid[piece_pos[0]][piece_pos[1]].color: #Get rid off the moves that attack allies
                to_remove.append(i)
        for i in to_remove:
            possible_moves.remove(i)
        
        return possible_moves 

    result = Piece(list_moves, "Q", "Queen", color)
    return result

class Board:
    """Object representing the board.
    It is not intended to change during execution"""

    def __init__(self, grid : list = "start", turn : int = 0, last_move : str = None, fen_list = [], last_capture = 0) -> None:
        self.turn = turn
        if grid == "start":
            self.grid = grid_from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR") #Starting pos in FEN format
        elif grid == "empty":
            self.grid = [[None for _ in range(8)]for _ in range(8)] #Empty grid
        else :
            if type(grid) == str:
                self.grid = grid_from_fen(grid) #If the argument 'grid' is a string, convert the string to a chessboard using grid_from_fen
            else:
                self.grid = grid
        self.last_move = last_move
        self.fen_list = fen_list
        self.last_capture = last_capture

    def __getitem__(self, key : tuple) -> Piece:
        """Return the piece at the pos on the board.
        This function is called with Board[key]"""

        if type(key) == str: #not supposed to happen
            key = name_to_int(key)
            print("Debug : An item as been getted with str key", self.grid[key[0]][key[1]])
        return self.grid[key[0]][key[1]]

    def __setitem__(self, key : int, value) -> None:
        """Set the value of a square on the board.
        This function is called with Board[key] = value"""
        
        if type(key) == str: #not supposed to happen
            key = name_to_int(key)
            print("Debug : An item as been setted with str key", self.grid[key[0]][key[1]])
        self.grid[key[0]][key[1]] = value

    def __repr__(self) -> str:
        """Return a string representing the board.
        This function is called with print(Board) or str(Board)"""

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
        """Return a copy of the grid with elements that are distinct from the original grid (it can be modified without changing the original)"""
        return [[self[row,col].copy() if self[row,col] != None else None for col in range(8)]for row in range(8)]

    def to_fen(self) -> str:
        """Return a string in FEN format representing the board"""

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
        """Return a Board object with a piece moved. The movement is a tuple of two tuples indicating the start position and the destination position."""

        new_board = Board(self.copy_grid(), (self.turn + 1)%2, movement, self.fen_list + [self.to_fen()], 0 if type(movement) == tuple and (self[movement[1]] != None or self[movement[0]].name == "Pawn") else self.last_capture + 1)

        if (movement == ((0, 4), (0, 6)) or movement == ((7, 4), (7, 6))) and self[movement[0]].name == "King" and self[movement[0]].can_castle: #Short castle 
            new_board[self.turn * 7,6], new_board[self.turn * 7,4] = new_board[self.turn * 7,4], None
            new_board[self.turn * 7,5], new_board[self.turn * 7,7] = new_board[self.turn * 7,7], None
            new_board[self.turn * 7,6].can_castle, new_board[self.turn * 7,5].can_castle = False, False

        elif (movement == ((0, 4), (0, 2)) or movement == ((7, 4), (7, 2))) and self[movement[0]].name == "King" and self[movement[0]].can_castle: #Long castle
            new_board[self.turn * 7,2], new_board[self.turn * 7,4] = new_board[self.turn * 7,4], None
            new_board[self.turn * 7,3], new_board[self.turn * 7,0] = new_board[self.turn * 7,0], None
            new_board[self.turn * 7,2].can_castle, new_board[self.turn * 7,3].can_castle = False, False
        else:

            start_pos, end_pos, arg = movement[0], movement[1], movement[2] if len(movement)>2 else None

            new_board[end_pos], new_board[start_pos] = new_board[start_pos], None
            if hasattr(new_board[end_pos], "can_castle"): #If the piece that moves can castle, now it can't
                new_board[end_pos].can_castle = False

            if arg != None:
                if "=" in arg: #Detect promotion
                    if arg[1] == "K":
                        new_board[end_pos] = knight(new_board[end_pos].color)
                    if arg[1] == "B":
                        new_board[end_pos] = bishop(new_board[end_pos].color)
                    if arg[1] == "R":
                        new_board[end_pos] = rook(new_board[end_pos].color, can_castle = False)
                    if arg[1] == "Q":
                        new_board[end_pos] = queen(new_board[end_pos].color)

                elif "&" in arg: #Detect en passant capture
                    new_board[int(movement[2][1]),int(movement[2][2])] = None

        return new_board

    def is_in_check(self, color, pos : tuple = "king_pos") -> bool:
        if pos == "king_pos":
            for row in range(8):
                for col in range(8):
                    if self[row,col] != None and self[row,col].name == "King" and self[row,col].color == color: #Search the king
                        pos = (row, col)
            if pos == "king_pos": #Case where the king would have disappeared from the chessboard (never happens in theory)
                raise Exception("The king is not foundable : "+ self.last_move)
        
        # Check all possible moves and see if any move ends at the King's position
        for i in self.get_all_possible_moves(False, False, (color+1)%2):
            if i[1] == pos:
                return True
        return False

    def get_state(self):
        """Return the state of the game (Victory, Defeat, Draw, Stalemate, ...), return "running" if the game is not finished"""

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
        """Return a list of all possible moves in this position"""

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
        """Return a list of possible moves for a given piece"""

        out = []
        for i in self.get_all_possible_moves():
            if i[0] == start_pos:
                out.append(i)
        return out

    def make_readeable(self, movement : tuple) -> str:
        """Return a string of the abbreviated algebraic notation of the move from this board"""

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
        """Assign a score to a board based on the game state (checkmate, stalemate, ...), the value of the pieces on it, and the freedom of movement of the pieces"""

        if len(self.get_all_possible_moves()) == 0:
            if self.is_in_check(self.turn) : #Checkmate
                if self.turn == 0:
                    return float("-inf") 
                else :
                    return float("inf")
            else :
                return 0 #Pat

        if self.fen_list.count(self.to_fen()) >= 2: #Draw by repetition
            return 0

        if self.last_capture >= 50: #50 moves rule
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
                            eval += value[self[row, col].letter] #Raw value of the piece
                            move_list = self[row, col].list_moves((row, col), self)
                            eval += len(move_list) / 30 #Freedom of movement
                            for i in move_list:
                                if self[i[1]] != None: #Bonus if the piece attacks or defends an important piece
                                    if self[i[1]].color == 0:
                                        eval += value[self[i[1]].letter] / 10 
                                    else :
                                        eval += value[self[i[1]].letter] / 10
                            remaining_white_pieces.append(self[row, col].letter)
                        else :
                            eval -= value[self[row, col].letter] #Raw value of the piece
                            move_list = self[row, col].list_moves((row, col), self)
                            eval -= len(move_list) / 30 #Freedom of movement
                            for i in move_list:
                                if self[i[1]] != None: #Bonus if the piece attacks or defends an important piece
                                    if self[i[1]].color == 1:
                                        eval -= value[self[i[1]].letter] / 10
                                    else :
                                        eval -= value[self[i[1]].letter] / 10
                            remaining_black_pieces.append(self[row, col].letter)
            
            white_is_in_material_deficiency = remaining_white_pieces.count("P") == remaining_white_pieces.count("Q") == remaining_white_pieces.count("R") == 0 and remaining_white_pieces.count("B") + remaining_white_pieces.count("N") <= 1
            black_is_in_material_deficiency = remaining_black_pieces.count("P") == remaining_black_pieces.count("Q") == remaining_black_pieces.count("R") == 0 and remaining_black_pieces.count("B") + remaining_black_pieces.count("N") <= 1

            if white_is_in_material_deficiency and black_is_in_material_deficiency : #Material deficiency
                return 0

        return round(eval, 1)

    def sorting_eval(self) -> int:
        """Very basic static evaluation used for sorting moves"""

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
        """Recursive evaluation using the alpha-beta algorithm"""

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
                    if best_move > b: #Alpha-beta pruning
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
                    if best_move < a: #Alpha-beta pruning
                        return best_move
            return best_move

    def choose_best_move(self, n) -> tuple:
        """Return the best move (as a tuple) based on recursive evaluation"""

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