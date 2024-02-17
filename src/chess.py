STARTING_POS = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

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

class Piece:
    """Object standing for pieces"""

    def __init__(self, type : str, color : int, can_castle : bool = False) -> None:
        self.type = type
        self.letter = "N" if type == "Knight" else type[0].upper()
        self.color = color
        self.can_castle = can_castle

    def get_color(self) -> str:
        if self.color == 0: 
            return "white"
        else :
            return "black"
    
    def get_letter(self) -> str:
        return self.letter
    
    def __repr__(self) -> str:
        return f"{self.type}, color : {self.get_color()} "
    
    def copy(self):
        return Piece(self.type, self.color, self.can_castle)

    def list_moves(self, piece_pos : tuple, board, try_castle : bool = True) -> list:
        """Function calculating all possible moves for the piece.
        This function will be added as an attribut"""

        color = self.color
        possible_moves = []
        dir = {"King" : [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)],
               "Pawn" : None,
               "Knight" : [(2, 1), (1, 2), (-2, 1), (-1, 2), (2, -1), (1, -2), (-2, -1), (-1, -2)],
               "Bishop" : [(1, 1), (1, -1), (-1, 1), (-1, -1)],
               "Rook" : [(0, 1), (0, -1), (1, 0), (-1, 0)],
               "Queen" : [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]}[self.type]
        
        if self.type in ("King", "Knight"):
            for i in dir: #List all the squares on which the piece can go
                if 0 <= i[0] + piece_pos[0] <= 7 and 0 <= i[1] + piece_pos[1] <= 7: #Check if that square is on the board
                    possible_moves.append(((piece_pos[0], piece_pos[1]),(i[0] + piece_pos[0], i[1] + piece_pos[1])))

        elif self.type in ("Bishop", "Rook", "Queen"):
            for i in dir: #List all possible directions for the piece
                current = piece_pos
                #Look in each direction and add the squares until reaching the edge of the board or encountering a piece
                while board.grid[current[0]][current[1]] == None or current == piece_pos : 
                    current = (current[0] + i[0], current[1] + i[1])
                    if current[0] < 0 or current[0] > 7 or current[1] < 0 or current[1] > 7: #Check if the square is on the board
                        break
                    else :
                        possible_moves.append(((piece_pos[0], piece_pos[1]),current))
        
        elif self.type == "Pawn":
            if piece_pos[0] == 1 + color * 5: #Move 2 squares forward for the pawn's first move
                if board[piece_pos[0]+1-2*color, piece_pos[1]] == board[piece_pos[0]+2-4*color, piece_pos[1]] == None:
                    possible_moves.append(((piece_pos[0], piece_pos[1]),(piece_pos[0]+2-4*color, piece_pos[1])))
            
            if board[piece_pos[0]+1-2*color, piece_pos[1]] == None : #Move 1 square forward
                possible_moves.append(((piece_pos[0], piece_pos[1]),(piece_pos[0]+1-2*color, piece_pos[1])))

            if piece_pos[1]+1 <= 7 and board[piece_pos[0]+1-2*color, piece_pos[1]+1] != None:
                possible_moves.append(((piece_pos[0], piece_pos[1]),(piece_pos[0]+1-2*color, piece_pos[1]+1))) #Capture diagonally to the right

            if piece_pos[1]-1 >= 0 and board[piece_pos[0]+1-2*color, piece_pos[1]-1] != None:
                possible_moves.append(((piece_pos[0], piece_pos[1]),(piece_pos[0]+1-2*color, piece_pos[1]-1))) #Capture diagonally to the left

            if board.last_move != None and board.last_move[1] == (piece_pos[0], piece_pos[1]+1) and board.last_move[0] == (piece_pos[0]+2-4*color, piece_pos[1]+1) and board[board.last_move[1]].type == "Pawn":
                possible_moves.append(((piece_pos[0], piece_pos[1]),(piece_pos[0]+1-2*color, piece_pos[1]+1), "&"+str(piece_pos[0])+str(piece_pos[1]+1))) #En passant capture to the right
            
            if board.last_move != None and board.last_move[1] == (piece_pos[0], piece_pos[1]-1) and board.last_move[0] == (piece_pos[0]+2-4*color, piece_pos[1]-1) and board[board.last_move[1]].type == "Pawn":
                possible_moves.append(((piece_pos[0], piece_pos[1]),(piece_pos[0]+1-2*color, piece_pos[1]-1), "&"+str(piece_pos[0])+str(piece_pos[1]-1))) #En passant capture to the left
        
        for i in possible_moves.copy():
            if board[i[1]] != None and board[i[1]].color == board.grid[piece_pos[0]][piece_pos[1]].color: #Get rid off the moves that attack allies
                possible_moves.remove(i)
            
        if self.type == "Pawn":
            for i in possible_moves.copy(): #Add promotion for first and last row
                if i[1][0] == 0 or i[1][0] == 7:
                    possible_moves.remove(i)
                    for j in ["N", "B", "R", "Q"]:
                        possible_moves.append(i+("="+j,))
        
        if self.type == "King" and try_castle:
            row = color * 7
            #Short castle
            if board[row, 4] != None and board[row, 4].type == "King" and board[row, 4].can_castle:
                if board[row, 7] != None and board[row, 7].type == "Rook" and board[row, 7].can_castle:
                    if board[row, 5] == board[row, 6] == None:
                        if board.is_in_check(color, (row, 4)) == board.is_in_check(color, (row, 5)) == board.is_in_check(color, (row, 6)) == False :
                            possible_moves.append(((color * 7, 4), (color * 7, 6)))
            #Long castle
            if board[row, 4] != None and board[row, 4].type == "King" and board[row, 4].can_castle:
                if board[row, 0] != None and board[row, 0].type == "Rook" and board[row, 0].can_castle:
                    if board[row, 3] == board[row, 2] == board[row, 1] == None:
                        if board.is_in_check(color, (row, 4)) == board.is_in_check(color, (row, 3)) == board.is_in_check(color, (row, 2)) == False :
                            possible_moves.append(((color * 7, 4), (color * 7, 2)))

        return possible_moves

class Board:
    """Object representing the board.
    It is not intended to change during execution, moving a piece with self.move() create an new instance of the board"""

    def __init__(self, grid : list = "start", turn : int = 0, last_move : str = None, fen_list = [], move_list = [], last_capture = 0) -> None:
        self.turn = turn
        self.grid = [[None for _ in range(8)]for _ in range(8)] #Empty grid
        self.last_capture = last_capture
        self.last_move = last_move
        self.fen_list = fen_list
        self.move_list = move_list

        if type(grid) == str:
            if grid == "start":
                grid = STARTING_POS #Starting pos in FEN format
            
            self.grid = [[None for _ in range(8)]for _ in range(8)]
            current = (7, 0)
            name = {"P" : "Pawn","N" : "Knight","B" : "Bishop","R" : "Rook","Q" : "Queen","K" : "King"}

            for i in grid.split(" ")[0]:
                if i == "/":
                    current = (current[0]-1, 0)
                elif i.isdigit():
                    current = (current[0], current[1]+int(i))
                elif i.upper() in name:
                    self.grid[current[0]][current[1]] = Piece(name[i.upper()],1 if i.islower() else 0, False)
                    current = (current[0], current[1]+1)
            
            if len(grid.split(" ")) >= 2:
                self.turn = int(grid.split(" ")[1] == "b")
            
            if len(grid.split(" ")) >= 3:
                if grid.split(" ")[2] != "-":
                    if "K" in grid.split(" ")[2]:
                        self[0, 4].can_castle = True
                        self[0, 7].can_castle = True
                    if "Q" in grid.split(" ")[2]:
                        self[0, 4].can_castle = True
                        self[0, 0].can_castle = True
                    if "k" in grid.split(" ")[2]:
                        self[7, 4].can_castle = True
                        self[7, 7].can_castle = True
                    if "q" in grid.split(" ")[2]:
                        self[7, 4].can_castle = True
                        self[7, 0].can_castle = True

            if len(grid.split(" ")) >= 4 and grid.split(" ")[3] != "-":
                move = name_to_int(grid.split(" ")[3])
                if self.turn != 0:
                    self.last_move = (move[0]-1, move[1]), (move[0]+1, move[1])
                else :
                    self.last_move = (move[0]+1, move[1]), (move[0]-1, move[1])

            if len(grid.split(" ")) >= 5:
                self.last_capture = int(grid.split(" ")[4])

            if len(grid.split(" ")) >= 6:
                self.fen_list = ["" for _ in range((int(grid.split(" ")[5])-1)*2+self.turn)]
        else:
            self.grid = grid

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

        #board representation
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
        out = out[:-1]
    
        return out

    def to_pgn(self) -> str:
        """Return a complete string in PGN format representing the moves mades from the beginning of the game"""
        if len(self.fen_list) <= 0 or self.fen_list[0] != STARTING_POS.split(" ")[0]:
            return 
        
        simulated_board = Board()
        out = ""
        for i in range(len(self.move_list)):
            out += " "
            if i%2 == 0:
                out += str(i//2+1)+". "
            out += simulated_board.make_readeable(self.move_list[i])
            simulated_board = simulated_board.move(self.move_list[i])
        
        if self.get_state() != "Running":
            out += " "+self.get_state()[1].replace(" ", "")

        return out[1:]
    
    def to_complete_fen(self) -> str:
        """Return a complete string in FEN format representing the board that can be recognize by chess programs"""

        out = self.to_fen()

        #Active color
        out += " "+("w" if self.turn == 0 else "b")

        #Castling
        castling_options = ""
        if self[0, 4] != None and self[0, 4].type == "King" and self[0, 4].can_castle: #Le roi blanc peut roquer
            if self[0, 7] != None and self[0, 7].type == "Rook" and self[0, 7].can_castle: #La tour coté dame peut roquer
                castling_options += "K"
            if self[0, 0] != None and self[0, 0].type == "Rook" and self[0, 0].can_castle: #La tour coté dame peut roquer
                castling_options += "Q"

        if self[7, 4] != None and self[7, 4].type == "King" and self[7, 4].can_castle: #Le roi noir peut roquer
            if self[7, 7] != None and self[7, 7].type == "Rook" and self[7, 7].can_castle: #La tour coté dame peut roquer
                castling_options += "k"
            if self[7, 0] != None and self[7, 0].type == "Rook" and self[7, 0].can_castle: #La tour coté dame peut roquer
                castling_options += "q"
        
        if castling_options == "":
            out += " -"
        else :
            out += " "+castling_options
        
        #En passant
        if self.last_move != None and self[self.last_move[1]].type == "Pawn" and abs(self.last_move[0][0]-self.last_move[1][0]) == 2:
            out += " "+int_to_name(self.last_move[1][0]+1-2*self.turn, self.last_move[1][1])
        else :
            out += " -"

        #Halfmove clock
        out += " "+str(self.last_capture)

        #Fullmove clock
        out += " "+str(len(self.fen_list)//2+1)
        
        return out

    def move(self, movement : tuple):

        """Return a Board object with a piece moved. The movement is a tuple of two tuples indicating the start position and the destination position."""

        new_board = Board(self.copy_grid(), (self.turn + 1)%2, movement, self.fen_list + [self.to_fen()], self.move_list + [movement],0 if type(movement) == tuple and (self[movement[1]] != None or self[movement[0]].type == "Pawn") else self.last_capture + 1)
        
        if (movement == ((0, 4), (0, 6)) or movement == ((7, 4), (7, 6))) and self[movement[0]].type == "King" and self[movement[0]].can_castle: #Short castle 
            new_board[self.turn * 7,6], new_board[self.turn * 7,4] = new_board[self.turn * 7,4], None
            new_board[self.turn * 7,5], new_board[self.turn * 7,7] = new_board[self.turn * 7,7], None
            new_board[self.turn * 7,6].can_castle, new_board[self.turn * 7,5].can_castle = False, False

        elif (movement == ((0, 4), (0, 2)) or movement == ((7, 4), (7, 2))) and self[movement[0]].type == "King" and self[movement[0]].can_castle: #Long castle
            new_board[self.turn * 7,2], new_board[self.turn * 7,4] = new_board[self.turn * 7,4], None
            new_board[self.turn * 7,3], new_board[self.turn * 7,0] = new_board[self.turn * 7,0], None
            new_board[self.turn * 7,2].can_castle, new_board[self.turn * 7,3].can_castle = False, False
        else:

            start_pos, end_pos, arg = movement[0], movement[1], movement[2] if len(movement)>2 else None

            new_board[end_pos], new_board[start_pos] = new_board[start_pos], None
            new_board[end_pos].can_castle = False

            if arg != None:
                if "=" in arg: #Detect promotion
                    if arg[1] == "N":
                        new_board[end_pos] = Piece("Knight", new_board[end_pos].color, can_castle = False)
                    if arg[1] == "B":
                        new_board[end_pos] = Piece("Bishop", new_board[end_pos].color, can_castle = False)
                    if arg[1] == "R":
                        new_board[end_pos] = Piece("Rook", new_board[end_pos].color, can_castle = False)
                    if arg[1] == "Q":
                        new_board[end_pos] = Piece("Queen", new_board[end_pos].color, can_castle = False)

                elif "&" in arg: #Detect en passant capture
                    new_board[int(movement[2][1]),int(movement[2][2])] = None

        return new_board

    def is_in_check(self, color, pos : tuple = "king_pos") -> bool:
        if pos == "king_pos":
            for row in range(8):
                for col in range(8):
                    if self[row,col] != None and self[row,col].type == "King" and self[row,col].color == color: #Search the king
                        pos = (row, col)
        
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
                    for move in self[row,col].list_moves((row, col), self, try_castle):
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

        if self[movement[0]].type == "King" and abs(movement[0][1]-movement[1][1]) == 2:
            if movement[0][1]-movement[1][1] == 2:
                return "O-O-O"
            else :
                return "O-O"

        out = ""
        if self[movement[0]].type != "Pawn" :
            out += self[movement[0]].letter
        
        other_starting_points = []
        for i in self.get_all_possible_moves():
            if i[1] == movement[1] and self[i[0]].type == self[movement[0]].type and i[0] != movement[0]:
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

    def make_unreadeable(self, movement : str) -> str:
        possible_moves = self.get_all_possible_moves()
        for i in range(len(possible_moves)):
            if self.make_readeable(possible_moves[i]) == movement:
                return possible_moves[i]
        raise Exception(f"impossible to convert : {movement}, no matching movement found")

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