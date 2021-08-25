from copy import deepcopy

class Chess:
    '''Contains all logic for a chess game'''
    def __init__(self, board=[
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'], #a8 - h8
            ['bP' for i in range(8)], [None for i in range(8)], [None for i in range(8)],
            [None for i in range(8)], [None for i in range(8)], ['wP' for i in range(8)],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR'], #a1 - h1
        ], allMoves=[], isWhitesMove=True, wCastled=False, wKingMoved=False,
        bCastled=False, bKingMoved=False, gameResult=None, wPoints=0, bPoints=0):
        """intializes the board and sets the state of the board"""
        self.board = board
        self.isWhitesMove = isWhitesMove
        self.allMoves = allMoves
        self.gameResult = gameResult
        self.whiteCastled = wCastled
        self.blackCastled = bCastled
        self.wKingMoved = wKingMoved
        self.bKingMoved = bKingMoved
        self.wPoints = wPoints
        self.bPoints = bPoints
        # TODO : add logic to create game string from all moves
    
    def __str__(game):
        '''prints the board on console'''
        board = ''
        for row in game.board:
            board += '| '
            for cell in row:
                if not cell: board+='  '
                elif cell[0]=='b': board += cell[1].lower()+' '
                elif cell[0]=='w': board += cell[1].upper()+' '
            board += '|\n'
        return board
    
    def gameOver(self):
        """
        checks for a result from the board.
        1  white won
        -1 black won
        0  draw
        2  quit
        """
        pass            

    def isCheck(game, check_side=None):
        '''Returns a boolean specifying if the next player is in check or not. If worb is set to w or b, checking is made for white or black respectively'''
        king, enemies = None, []
        if not check_side: check_side = 'w' if game.isWhitesMove else 'b'
        for y, row in enumerate(game.board):
            for x, cell in enumerate(row):
                if cell[0] != check_side: enemies.append((x, y))
                elif cell[0] == check_side and cell[1]=='K': king = (x, y)
        
        for enemy in enemies:
            if game.canTake(enemy, king):
                return True

    def getMoves(game, current_side=None):
        '''Returns a list of possible moves (pairs of xy coordinate pairs)'''
        if not current_side:
            current_side = 'w' if game.isWhitesMove else 'b'
        pieces = [
            (x, y) for y, row in enumerate(game.board)
            for x, cell in enumerate(row) if cell!=None and cell[0]==current_side]
        return [
            (piece, move) for piece in pieces
            for move in game.movesOf(*piece)]
    
    def legalMoves(self, cell, piece=None):
        '''Returns a list of legal moves for a piece in the cell.
        if piece (PRNBQK) is explicitly specified the rules of that piece would apply.
        This method does not consider the state of the game.'''

        if type(cell)==str: x, y = self.getCoords(cell)
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
                ops.append((k, y))
                ops.append((x, k))
            ops.remove((x, y))

        elif piece[1] == 'N':
            ops = [
                self.board[dy][dx] for dy in range(y-2, y+3) for dx in range(x-2, x+3)
                if 0<=dx<8 and 0<=dy<8 and dx!=x and dy!=y and abs(dx-x)!=abs(dy-y)
            ]

        elif piece[1] == 'B':
            for k in range(0, 8):
                if 0 <= y-(x-k) < 8:
                    ops.append((k, y-(x-k)))
                if 0 <= y+(x-k) < 8:
                    ops.append((k, y+(x-k)))

        elif piece[1] == 'Q':
            return self.legalMoves(x, y, current_side+'B') + self.legalMoves(x, y, current_side+'R')

        elif piece[1] == 'K':
            ops = [
                (dx, dy) for dy in range(y-1, y+2)
                for dx in range(x-1, x+2)
                if 0<=dy<8 and 0<=dx<8
            ] - [(x, y)]
            # castling
            kingMoved = self.wKingMoved if current_side=='w' else self.bKingMoved
            if not kingMoved: ops+=[(x+2, y), (x-2, y)]

        return ops
    
    def movesOf(self, cell, piece=None):
        '''Returns a list of valid moves for a piece in the cell.
        This method simply refines the moves from legalMoves according to the game.'''
        
        if type(cell)==str: x, y = self.getCoords(cell)
        else: x, y = cell[0], cell[1]
        if not piece:
            if not self.board[y][x]: return []
            else: piece = self.board[y][x]
        current_side = piece[0]
        moves, ops = self.legalMoves(cell, piece), []

        if piece[1] == 'P':
            if current_side=='w' and y>0: d=-1
            elif current_side=='b' and y<7: d=1
            else: return []

            for op in moves:
                lastMove = self.allMoves[-1]
                if (((not self.board[op[1]][op[0]] or # empty cell
                self.board[op[1]][op[0]][0] != current_side) and # oponent in cell
                (abs(op[1]-y)==1 or self.board[y+d][x]==self.board[y+2*d][x]==None)) or # first move vals
                (((d==1 and y==4 and lastMove[0][1]==6) or (d==-1 and y==3 and lastMove[0][1]==1)) \
                and abs(lastMove[0][0]-x)==1 and lastMove[0][0]==lastMove[1][0] and lastMove[1][1]==y)): #en passant
                    ops.append(op)

        elif piece[1] == 'R':
            e, w, n, s = x, x, y, y # saves the longest distance a rook can go
            for d in range(1, 8):
                if e==x and x+d<8 and self.board[y][x+d]:
                    if self.board[y][x+d][0]!=current_side: e=x+d
                    elif self.board[y][x+d][0]==current_side: e=x+d-1
                if w==x and x-d>=0 and self.board[y][x-d]:
                    if self.board[y][x-d][0]!=current_side: w=x-d
                    elif self.board[y][x-d][0]==current_side: w=x-d+1
                if s==y and y+d<8 and self.board[y+d][x]:
                    if self.board[y+d][x][0]!=current_side: s=y+d
                    elif self.board[y+d][x][0]==current_side: s=y+d-1
                if n==y and y-d>=0 and self.board[y-d][x]:
                    if self.board[y-d][x][0]!=current_side: n=y-d
                    elif self.board[y-d][x][0]==current_side: n=y-d+1
            ops = [op for op in moves if w<=op[0]<=e and n<=op[1]<=s]

        elif piece[1] == 'N':
            ops = [op for op in moves if self.board[op[0]][op[1]][0]!=current_side]

        elif piece[1] == 'B':
            ne, nw, se, sw = 0, 0, 0, 0 # saves the longest distance a bishop can go
            for d in range(1, 8):
                if ne==0 and 0<=x+d<8 and 0<=y-d<8 and self.board[y-d][x+d]:
                    if self.board[y-d][x+d][0]!=current_side: ne=d
                    elif self.board[y-d][x+d][0]==current_side: ne=d-1
                if nw==0 and 0<=x-d<8 and 0<=y-d<8 and self.board[y-d][x-d]:
                    if self.board[y-d][x-d][0]!=current_side: nw=d
                    elif self.board[y-d][x-d][0]==current_side: nw=d-1
                if se==0 and 0<=x+d<8 and 0<=y+d<8 and self.board[y+d][x+d]:
                    if self.board[y+d][x+d][0]!=current_side: se=d
                    elif self.board[y+d][x+d][0]==current_side: se=d-1
                if sw==0 and 0<=x-d<8 and 0<=y+d<8 and self.board[y+d][x-d]:
                    if self.board[y+d][x-d][0]!=current_side: sw=d
                    elif self.board[y+d][x-d][0]==current_side: sw=d-1
            ops = [
                op for op in moves
                if (x+ne>=op[0]>x and y-ne<=op[1]<y)
                or (x-nw<=op[0]<x and y-nw<=op[1]<y)
                or (x+se>=op[0]>x and y+se>=op[1]>y)
                or (x-se<=op[0]<x and y+sw>=op[1]>y)
            ]

        elif piece[1] == 'Q':
            return self.movesOf(x, y, current_side+'B') + self.movesOf(x, y, current_side+'R')

        elif piece[1] == 'K':
            kingMoved = self.hasMoved((4, 7)) if current_side=='w' else self.hasMoved((4, 0))
            for op in moves:
                if op[0]-x in (1, -1) and (
                    not self.board[op[1]][op[0]]
                    or self.board[op[1]][op[0]][0]!=current_side):
                    ops.append(op)
                elif not kingMoved and not self.isCheck(): # castling conditions
                    if op[0]-x == 2 and not self.hasMoved((7, y)) and \
                    self.board[y][5]==self.board[y][6]==None and \
                    not self.makeMove((4, y), (5, y)).isCheck() :
                        ops += [(6, y)]
                    elif op[0]-x == -2 and not self.hasMoved((0, y)) and \
                    self.board[y][1]==self.board[y][2]==self.board[y][3]==None and \
                    not self.makeMove((4, y), (3, y)).isCheck() :
                        ops += [(2, y)]

        # validate pinned moves
        return [option for option in ops if not self.board.makeMove((x,y), option).isCheck(current_side)]
    
    def canTake(game, cell, target):
        '''Returns a boolean that tells if a piece in a cell can acquire/take the target cell in a move'''
        return target in game.movesOf(cell)
    
    def getCoords(game, string):
        '''Accepts a string Chess-cell location and returns x-y tuple indices on the board'''
        return (
            {ch:i for i, ch in enumerate('abcdefgh')}[string[0].lower()],
            8-int(string[1])
        )
    
    def hasMoved(game, cell):
        '''Returns a boolean that tells wether or not a move has been made from the cell during the game'''
        if type(cell)==str: x, y = game.getCoords(cell)
        else: x, y = cell[0], cell[1]
        for move in game.allMoves:
            if move[0] == cell:
                return True
        return False
    
    def makeMove(game, oldCell, newCell):
        '''Returns an instance of the board after having made the move'''
        if type(oldCell) == str: oldCell = game.getCoords(oldCell)
        if type(newCell) == str: newCell = game.getCoords(newCell)
        
        if not game.board[oldCell[1]][oldCell[0]] \
        or game.board[oldCell[1]][oldCell[0]][0]=='w' and not game.isWhitesMove \
        or game.board[oldCell[1]][oldCell[0]][0]=='b' and game.isWhitesMove: return game

        current_side = game.board[oldCell[1]][oldCell[0]][0]
        if game.board[newCell[1]][newCell[0]]!=None:
            if game.board[newCell[1]][newCell[0]][0]!=current_side:
                pass # TODO: add points for piece acquired
            else: # cannot move to own piece's square
                return game

        g = deepcopy(game)

        #king moves
        if g.board[oldCell[1]][oldCell[0]][1]=='K':
            if g.board[oldCell[1][oldCell[0]]][0]=='w': g.wKingMoved = True
            else: g.bKingMoved = True
            if abs(oldCell[0]-newCell[0])>1:
                if g.board[oldCell[1][oldCell[0]]][0]=='w': g.whiteCastled = True
                else: g.blackCastled = True
        #en passant
        elif g.board[oldCell[1]][oldCell[0]][1]=='P' and \
            abs(oldCell[0]-newCell[0])==abs(oldCell[1]-newCell[1])==1 and \
            g.board[newCell[1]][oldCell[0]] == None:
            g.board[newCell[1]][oldCell[0]] = None
            # TODO: add game points for en passant
    
        g.board[newCell[1]][newCell[0]] = g.board[oldCell[1]][oldCell[0]]
        g.board[oldCell[1]][oldCell[0]] = None
        g.isWhitesMove = not g.isWhitesMove
        g.allMoves.append((oldCell, newCell)) # TODO: convert matrix history to string history
        
        #pawn promotion
        if g.board[newCell[1]][newCell[0]][1]=='P' and newCell[1] in (0, 7):
            g.promotePawn(newCell, g.choosePromotion())
        # TODO: remove next line
        print(g)
        return g
    
    def promotePawn(game, cell, newPiece):
        '''Promotes pawn to newPiece. Contains all logic to represent promotion in the logs.
        This method is intended to be called just after the move is recorded in the game log.'''
        if cell[1] not in (0, 7): return False
        if newPiece not in 'RNBQ': return False
        game.board[cell[1]][cell[0]][1] = newPiece
        # TODO: add promotion to game logs
    
    def choosePromotion(game):
        '''Contains all logic to pass control to the user to return the Piece to promote to
        Intended to be overriden so that UI could control
        Expects a character in the set {R, N, B, Q} to be return'''
        return input('Input chess piece to promote to (R, N, B, Q) : ')




