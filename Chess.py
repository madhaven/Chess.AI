from copy import deepcopy

class Chess:
    '''Contains all logic for a chess game'''
    def __init__(self, choosePiece=None, board=[
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'], #a8 - h8
            ['bP' for i in range(8)], [None for i in range(8)], [None for i in range(8)],
            [None for i in range(8)], [None for i in range(8)], ['wP' for i in range(8)],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR'], #a1 - h1
        ], log=[], isWhitesMove=True, gameResult=None, wPoints=0, bPoints=0):
        """intializes the board and sets the state of the board.

        The choosePiece argument expects a function that returns a character in (Q, R, B, N).
        This function will be used when a pawn is to be promoted. If choosePiece defaults to None,
        the pawn will be promoted to Queen."""
        self.board = board
        self.isWhitesMove = isWhitesMove
        self.log = log
        self.result = gameResult
        self.wPoints = wPoints
        self.bPoints = bPoints
        self.choosePiece = choosePiece if choosePiece else lambda:'Q'
        # TODO : add logic to create game string from all moves
        # TODO : add static method to initialize game from such a game log
    
    def __str__(game):
        '''prints the board on console'''
        string = ''
        for y, row in enumerate(game.board):
            string += '%d| '%(8-y)
            for cell in row:
                if not cell: string += '  '
                elif cell[0]=='b': string += cell[1].lower()+' '
                elif cell[0]=='w': string += cell[1].upper()+' '
            string += '|\n'
        string += '   a b c d e f g h\n'
        return string
    
    def checkResult(game):
        """
        checks for a result from the board.
        1  white won
        -1 black won
        0  draw
        2  quit
        """
        if not game.getMoves():
            if game.isCheck():
                if game.isWhitesMove: game.result = -1
                else: game.result = 1
            else: game.result = 0
        else: return False
        return game.result

    def isCheck(game, check_side=None):
        '''Returns a boolean specifying if the current player is in check or not.
        If check_side is set to w or b, checking is made for white or black respectively.'''
        # TODO: add parameter to check. so self moves don't need to brute force through options
        if not check_side: check_side = 'w' if game.isWhitesMove else 'b'
        for y, row in enumerate(game.board):
            for x, cell in enumerate(row):
                if game.board[y][x]==check_side+'K':
                    king=(x, y)
                    break
            else: continue
            break
        for checkPiece in ['P', 'RQ', 'BQ', 'N', 'K']:
            for coord in game.checkableMoves(king, check_side+checkPiece[0]):
                #essentially places a piece in kings cell and finds same enemy pieces in sight
                piece = game.board[coord[1]][coord[0]]
                if piece and piece[0]!=check_side and piece[1] in checkPiece:
                    return True
        return False

    def getMoves(game, current_side=None):
        '''Returns a list of possible moves (pairs of xy coordinate pairs)'''
        if not current_side: current_side = 'w' if game.isWhitesMove else 'b'
        pieces = [
            (x, y) for y, row in enumerate(game.board)
            for x, cell in enumerate(row) if cell!=None and cell[0]==current_side]
        return [
            (piece, move) for piece in pieces
            for move in game.movesOf(piece)]
    
    def legalMoves(self, cell, piece=None):
        '''Returns a list of legal moves for a piece in the cell.
        if piece (PRNBQK) is explicitly specified the rules of that piece would apply.
        This method does not consider the state of the game, only the position of the piece.
        Intended to be used when making PreMoves.'''
        if type(cell)==str: x, y = self.coords(cell)
        else: x, y = cell[0], cell[1]
        if not piece:
            if not self.board[y][x]: return []
            else: piece = self.board[y][x]
        current_side = piece[0]
        ops = []

        if piece[1] == 'P':
            if current_side=='w' and y>0: d=-1
            elif current_side=='b' and y<7: d=1
            else: return []
            
            ops += [(x, y+d)]
            if (d==1 and y==1) or (d==-1 and y==6): ops += [(x, y+d*2)]
            if x>0: ops += [(x-1, y+d)]
            if x<7: ops += [(x+1, y+d)]

        elif piece[1] == 'R':
            for k in range(0, 8):
                if k!=x: ops.append((k, y))
                if k!=y: ops.append((x, k))

        elif piece[1] == 'N':
            ops = [
                (dx, dy) for dy in range(y-2, y+3) for dx in range(x-2, x+3)
                if 0<=dx<8 and 0<=dy<8 and dx!=x and dy!=y and abs(dx-x)!=abs(dy-y)
            ]

        elif piece[1] == 'B':
            for k in range(0, 8):
                if 0 <= y-(x-k) < 8 and k!=x:
                    ops.append((k, y-(x-k)))
                if 0 <= y+(x-k) < 8 and k!=x:
                    ops.append((k, y+(x-k)))

        elif piece[1] == 'Q':
            return self.legalMoves((x, y), current_side+'B') + self.legalMoves((x, y), current_side+'R')

        elif piece[1] == 'K':
            ops = [
                (dx, dy) for dy in range(y-1, y+2)
                for dx in range(x-1, x+2)
                if 0<=dy<8 and 0<=dx<8
            ]
            ops.remove((x, y))
        
        return ops
    
    def checkableMoves(self, cell, piece=None):
        '''Returns a list of squares eyed/targetted by a piece in the cell, 
        This method simply refines the moves from legalMoves according to the game.
        This method Does not however check if the move is completely possible.'''
        
        if type(cell)==str: x, y = self.coords(cell)
        else: x, y = cell[0], cell[1]
        if not piece:
            if not self.board[y][x]: return []
            else: piece = self.board[y][x]
        current_side = piece[0]
        ops, moves = [], self.legalMoves((x, y), piece)

        if piece[1] == 'P':
            for op in moves:
                if op[0]-x in (1, -1): #sideways move
                    ops.append(op)

        elif piece[1] == 'R':
            for d in range(x+1, 8):
                ops.append((d, y))
                if self.board[y][d]: break
            for d in range(x-1, -1, -1):
                ops.append((d, y))
                if self.board[y][d]: break
            for d in range(y+1, 8):
                ops.append((x, d))
                if self.board[d][x]: break
            for d in range(y-1, -1, -1):
                ops.append((x, d))
                if self.board[d][x]: break

        elif piece[1] == 'N':
            ops = moves

        elif piece[1] == 'B':
            for d in range(1, min(8-x, 8-y)):
                ops.append((x+d, y+d))
                if self.board[y+d][x+d]: break
            for d in range(1, min(8-x, y+1)):
                ops.append((x+d, y-d))
                if self.board[y-d][x+d]: break
            for d in range(1, min(x+1, y+1)):
                ops.append((x-d, y-d))
                if self.board[y-d][x-d]: break
            for d in range(1, min(x+1, 8-y)):
                ops.append((x-d, y+d))
                if self.board[y+d][x-d]: break

        elif piece[1] == 'Q':
            ops = self.checkableMoves((x, y), current_side+'B') + self.checkableMoves((x, y), current_side+'R')

        elif piece[1] == 'K':
            ops = [
                op for op in moves
                if op[0]-x in (-1, 0, 1)
            ]
        return ops
    
    def movesOf(game, cell, piece=None):
        '''implements a check to make sure a piece can move from its current location.
        Also adds special checks for the pawn and the king's moves'''
        if type(cell)==str: x, y = game.coords(cell)
        else: x, y = cell[0], cell[1]
        if not piece:
            if not game.board[y][x]: return []
            else: piece = game.board[y][x]
        
        current_side = piece[0]
        moves = []
        
        if piece[1]=='P':
            for op in game.legalMoves((x, y), piece):
                if op[0]-x == 0: # straight move
                    if not game.board[op[1]][op[0]]: # empty square
                        if op[1]-y in (1, -1):
                            moves.append(op) # one step
                        elif op[1]-y in (2, -2) and not game.board[(op[1]+y)//2][op[0]]:
                            moves.append(op) # two steps and empty path
                else: # sidemove
                    if game.board[op[1]][op[0]] and game.board[op[1]][op[0]][0]!=current_side: #takes
                        ('takes', game.board[y][x], game.board[op[1]][op[0]])
                        moves.append(op)
                    elif len(game.log)>0 and y==(3 if current_side=='w' else 4) and\
                        op[1]==(game.log[-1][0][1]+game.log[-1][1][1])/2 and\
                        game.log[-1][0][0]==game.log[-1][1][0]==op[0]:
                            # en passant
                            moves.append(op)
        else: moves = game.checkableMoves((x, y), piece)

        if piece[1]=='K':
            # add castling moves
            kingMoved = game.hasMoved((4, 0)) if current_side=='b' else game.hasMoved((4, 7))
            if not kingMoved and not game.isCheck():
                if not game.hasMoved((7, y)) and \
                game.board[y][5]==game.board[y][6]==None and \
                not game.makeMove((4, y), (5, y), True).isCheck(current_side) :
                    moves.append((6, y))
                if not game.hasMoved((0, y)) and \
                game.board[y][1]==game.board[y][2]==game.board[y][3]==None and \
                not game.makeMove((4, y), (3, y), True).isCheck(current_side) :
                    moves.append((2, y))

        # ensure proposed move doesn't have a friendly piece on it and don't result in check
        finalMoves = [ 
            move for move in moves 
            if (not game.board[move[1]][move[0]] or game.board[move[1]][move[0]][0]!=current_side)
            and not game.makeMove((x,y), move, True).isCheck(current_side)
        ]
        return finalMoves
    
    def coords(game, string):
        '''Accepts a string Chess-cell location and returns x-y tuple indices on the board'''
        return (
            {ch:i for i, ch in enumerate('abcdefgh')}[string[0].lower()],
            8-int(string[1])
        )
    
    def notation(game, cell):
        '''Accepts a duplet cell, array location and returns a string notation of the cell'''
        return 'abcdefgh'[cell[0]]+str(8-cell[1])
    
    def hasMoved(game, cell):
        '''Returns a boolean that tells wether or not a move has been made from the cell during the game'''
        if type(cell)==str: x, y = game.coords(cell)
        else: x, y = cell[0], cell[1]
        for move in game.log:
            if move[0] == (x,y):
                return True
        return False
    
    def makeMove(game, oldCell, newCell, testMove=False):
        '''Returns an instance of the board after having made the move'''
        if type(oldCell) == str: oldCell = game.coords(oldCell)
        if type(newCell) == str: newCell = game.coords(newCell)
        
        if not game.board[oldCell[1]][oldCell[0]] \
        or (game.board[oldCell[1]][oldCell[0]][0]=='w' and not game.isWhitesMove) \
        or (game.board[oldCell[1]][oldCell[0]][0]=='b' and game.isWhitesMove):
            return game

        current_side = game.board[oldCell[1]][oldCell[0]][0]
        if game.board[newCell[1]][newCell[0]]:
            if game.board[newCell[1]][newCell[0]][0]!=current_side:
                pass # TODO: add points for piece acquired
            else: # cannot move to own piece's square
                return game

        g = deepcopy(game)

        #en passant
        if len(game.log)>0 and oldCell[1]==(3 if current_side=='w' else 4) and\
            newCell[1]==(game.log[-1][0][1]+game.log[-1][1][1])/2 and\
            game.log[-1][0][0]==game.log[-1][1][0]==newCell[0]:
            # print('enpessant acquired ', g.notation((newCell[0], oldCell[1])), g.board[newCell[0]][oldCell[1]])
            g.board[oldCell[1]][newCell[0]] = None
            # TODO: add game points for en passant
        
        #castling
        elif g.board[oldCell[1]][oldCell[0]][1]=='K' and not g.hasMoved(oldCell):
            if oldCell[0]-newCell[0] == 2: #queenside
                if not g.hasMoved((0, oldCell[1])):
                    g.board[oldCell[1]][3]=current_side+'R'
                    g.board[oldCell[1]][0]=None
            elif oldCell[0]-newCell[0] == -2: #kingside
                if not g.hasMoved((7, oldCell[1])):
                    g.board[oldCell[1]][5]=current_side+'R'
                    g.board[oldCell[1]][7]=None

        # the move
        g.board[newCell[1]][newCell[0]] = g.board[oldCell[1]][oldCell[0]]
        g.board[oldCell[1]][oldCell[0]] = None
        g.isWhitesMove = not g.isWhitesMove

        #pawn promotion
        if g.board[newCell[1]][newCell[0]][1]=='P' and newCell[1] in (0, 7):
            newPiece = g.choosePiece() if not testMove else 'P'
            if newPiece in 'RNBQ':
                print(current_side, newPiece)
                g.board[newCell[1]][newCell[0]] = current_side + newPiece
            else: return game
        # TODO: add promotion to game logs

        #game states
        g.log.append((oldCell, newCell)) # TODO: convert matrix history to string history
        if not testMove: g.checkResult()
        
        return g
    
    def save(game):
        '''Saves the log of the game into a text file'''
        from datetime import datetime
        now = datetime.now()
        filename = 'chess_%d%02d%02d%02d%02d%02d.save.txt'%(now.year, now.month, now.day, now.hour, now.minute, now.second)
        with open(filename, 'w') as file:
            for i, log in enumerate(game.log):
                file.write('%d. %s-%s\n'%(i+1, game.notation(log[0]), game.notation(log[1])))
        #TODO: add refined notation with piece info and promotion and takes
        return filename
    
    def load(game, filename):
        '''Loads a game state from a file'''
        # TODO: manage file saving formats in accordance with save method