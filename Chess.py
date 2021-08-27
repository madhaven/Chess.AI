from copy import deepcopy
from typing import final

class Chess:
    '''Contains all logic for a chess game'''
    def __init__(self, board=[
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'], #a8 - h8
            ['bP' for i in range(8)], [None for i in range(8)], [None for i in range(8)],
            [None for i in range(8)], [None for i in range(8)], ['wP' for i in range(8)],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR'], #a1 - h1
        ], log=[], isWhitesMove=True, gameResult=None, wPoints=0, bPoints=0):
        """intializes the board and sets the state of the board"""
        self.board = board
        self.isWhitesMove = isWhitesMove
        self.log = log
        self.gameResult = gameResult
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
    
    def gameOver(game):
        """
        checks for a result from the board.
        1  white won
        -1 black won
        0  draw
        2  quit
        """
        if not game.getMoves():
            if game.isCheck():
                if game.isWhitesMove: return -1
                else: return 1
        else: return 0

    def isCheck(game, check_side=None):
        '''Returns a boolean specifying if the next player is in check or not. If worb is set to w or b, checking is made for white or black respectively.
        As of now a brute force check is being carried out.
        It would be more computationally efficient to trace enemies from the kings point of view.'''
        king, enemies = None, []
        if not check_side: check_side = 'w' if game.isWhitesMove else 'b'
        for y, row in enumerate(game.board):
            for x, cell in enumerate(row):
                if cell:
                    if cell[0] != check_side: enemies.append((x, y))
                    elif cell[0] == check_side and cell[1]=='K': king = (x, y)
        
        #TODO: del the nex tline
        # print('CHECKING FOR CHECKS')

        for enemy in enemies:
            if king in game.checkableMoves(enemy):
                return True
        return False

    def getMoves(game, current_side=None):
        '''Returns a list of possible moves (pairs of xy coordinate pairs)'''
        if not current_side:
            current_side = 'w' if game.isWhitesMove else 'b'
        pieces = [
            (x, y) for y, row in enumerate(game.board)
            for x, cell in enumerate(row) if cell!=None and cell[0]==current_side]

        #TODO: del the following bock
        # print('pieces : ', pieces)
        # for piece in pieces:
        #     print('moves of', game.board[piece[1]][piece[0]])
        #     print(game.movesOf(piece))
        
        return [
            (piece, move) for piece in pieces
            for move in game.movesOf(piece)]
    
    def legalMoves(self, cell, piece=None):
        '''Returns a list of legal moves for a piece in the cell.
        if piece (PRNBQK) is explicitly specified the rules of that piece would apply.
        This method does not consider the state of the game, only the position of the piece.
        Intended to be used when making PreMoves.'''
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
        
        # print('legal moves', self.board[y][x], ops)
        return ops
    
    def checkableMoves(self, cell, piece=None):
        '''Returns a list of squares eyed/targetted by a piece in the cell, 
        This method simply refines the moves from legalMoves according to the game.
        This method Does not however check if the move is completely possible.'''
        
        if type(cell)==str: x, y = self.getCoords(cell)
        else: x, y = cell[0], cell[1]
        if not piece:
            if not self.board[y][x]: return []
            else: piece = self.board[y][x]
        current_side = piece[0]
        ops, moves = [], self.legalMoves(cell, piece)

        if piece[1] == 'P':
            for op in moves:
                if op[0]-x in (1, -1): #sideways move
                    ops.append(op)

        elif piece[1] == 'R':
            e, w, n, s = x, x, y, y # saves the longest distance a rook can go
            for d in range(1, 8):
                if e==x and x+d<8 and self.board[y][x+d]: e=x+d
                if w==x and x-d>=0 and self.board[y][x-d]: w=x-d
                if s==y and y+d<8 and self.board[y+d][x]: s=y+d
                if n==y and y-d>=0 and self.board[y-d][x]: n=y-d
            ops = [op for op in moves if w<=op[0]<=e and n<=op[1]<=s]

        elif piece[1] == 'N':
            ops = moves

        elif piece[1] == 'B':
            ne, nw, se, sw = 0, 0, 0, 0 # saves the longest distance a bishop can go
            for d in range(1, 8):
                if ne==0 and 0<=x+d<8 and 0<=y-d<8 and self.board[y-d][x+d]: ne=d
                if nw==0 and 0<=x-d<8 and 0<=y-d<8 and self.board[y-d][x-d]: nw=d
                if se==0 and 0<=x+d<8 and 0<=y+d<8 and self.board[y+d][x+d]: se=d
                if sw==0 and 0<=x-d<8 and 0<=y+d<8 and self.board[y+d][x-d]: sw=d
            ops = [
                op for op in moves
                if (x+ne>=op[0]>x and y-ne<=op[1]<y)
                or (x-nw<=op[0]<x and y-nw<=op[1]<y)
                or (x+se>=op[0]>x and y+se>=op[1]>y)
                or (x-se<=op[0]<x and y+sw>=op[1]>y)
            ]

        elif piece[1] == 'Q':
            ops = self.checkableMoves((x, y), current_side+'B') + self.checkableMoves((x, y), current_side+'R')

        elif piece[1] == 'K':
            ops = [
                op for op in moves
                if op[0]-x in (-1, 0, 1)
            ]
        
        #TODO: remove the next line
        # print('returning checkable moves of', self.board[y][x], ops)
        return ops
    
    def movesOf(game, cell, piece=None):
        '''implements a check to make sure a piece can move from its current location.
        Also adds special checks for the pawn and the king's moves'''
        if type(cell)==str: x, y = game.getCoords(cell)
        else: x, y = cell[0], cell[1]
        if not piece:
            if not game.board[y][x]: return []
            else: piece = game.board[y][x]
        current_side = piece[0]
        moves = []

        #TODO: del next line
        # print('checkablemoves of', game.board[cell[1]][cell[0]], ops)
        
        if piece[1]=='P':
            ops = game.legalMoves(cell, piece)
            for op in ops:
                if op[0]-x == 0 and not game.board[op[1]][op[0]]: #straight move to empty square
                    if op[1]-y in (1, -1): moves.append(op)
                    elif op[1]-y in (2, -2) and not game.board[(op[1]+y)//2][op[0]]:
                        moves.append(op) # two steps and empty path
                else: # sidemove
                    if not game.board[op[1]][op[0]] and len(game.log)>0: # en passant
                        lastMove = game.log[-1] 
                        if lastMove[1][1]==y and lastMove[0][0]==lastMove[1][0] and lastMove[0][0] in (x-1, x+1):
                            moves.append(op)
                    elif game.board[op[1]][op[0]] and game.board[op[1]][op[0]][0]!=current_side:
                        moves.append(op)
        else: 
            ops = game.checkableMoves(cell, piece)
            moves = ops
                      
        if piece[1]=='K':
            # add castling moves
            kingMoved = game.hasMoved((4, 0)) if current_side=='b' else game.hasMoved((4, 7))
            if not kingMoved and not game.isCheck():
                if not game.hasMoved((7, y)) and \
                game.board[y][5]==game.board[y][6]==None and \
                not game.makeMove((4, y), (5, y)).isCheck() :
                    moves.append((6, y))
                elif  not game.hasMoved((0, y)) and \
                game.board[y][1]==game.board[y][2]==game.board[y][3]==None and \
                not game.makeMove((4, y), (3, y)).isCheck() :
                    moves.append((2, y))

        # ensure proposed move doesn't have a friendly piece on it and don't result in check
        finalMoves = [ 
            move for move in moves 
            if (not game.board[move[1]][move[0]]
            or game.board[move[1]][move[0]][0]!=current_side)
            and not game.makeMove(cell, move).isCheck(current_side)
        ]

        #TODO: del nex tline
        # print('fianl moves of', game.board[cell[1]][cell[0]], finalMoves)
        return finalMoves
    
    def getCoords(game, string):
        '''Accepts a string Chess-cell location and returns x-y tuple indices on the board'''
        return (
            {ch:i for i, ch in enumerate('abcdefgh')}[string[0].lower()],
            8-int(string[1])
        )
    
    def getCell(game, cell):
        '''Accepts a duplet cell location and returns a string notation of the cell'''
        return 'abcdefgh'[cell[0]]+str(8-cell[1])
    
    def hasMoved(game, cell):
        '''Returns a boolean that tells wether or not a move has been made from the cell during the game'''
        if type(cell)==str: x, y = game.getCoords(cell)
        else: x, y = cell[0], cell[1]
        for move in game.log:
            if move[0] == cell:
                return True
        return False
    
    def makeMove(game, oldCell, newCell):
        '''Returns an instance of the board after having made the move'''
        if type(oldCell) == str: oldCell = game.getCoords(oldCell)
        if type(newCell) == str: newCell = game.getCoords(newCell)
        
        if not game.board[oldCell[1]][oldCell[0]] \
        or (game.board[oldCell[1]][oldCell[0]][0]=='w' and not game.isWhitesMove) \
        or (game.board[oldCell[1]][oldCell[0]][0]=='b' and game.isWhitesMove) \
        or newCell not in game.movesOf(oldCell): return game

        g = deepcopy(game)
        current_side = game.board[oldCell[1]][oldCell[0]][0]

        if game.board[newCell[1]][newCell[0]]:
            if game.board[newCell[1]][newCell[0]][0]!=current_side:
                pass # TODO: add points for piece acquired
            else: # cannot move to own piece's square
                return game

        #en passant
        if g.board[oldCell[1]][oldCell[0]][1]=='P' and \
            abs(oldCell[0]-newCell[0])==abs(oldCell[1]-newCell[1])==1 and \
            g.board[newCell[1]][oldCell[0]] == None:
            g.board[newCell[1]][oldCell[0]] = None
            # TODO: add game points for en passant
        
        #castling
        # TODO: shift rooks position in castling
    
        g.board[newCell[1]][newCell[0]] = g.board[oldCell[1]][oldCell[0]]
        g.board[oldCell[1]][oldCell[0]] = None
        g.isWhitesMove = not g.isWhitesMove
        g.log.append((oldCell, newCell)) # TODO: convert matrix history to string history
        
        #pawn promotion
        if g.board[newCell[1]][newCell[0]][1]=='P' and newCell[1] in (0, 7):
            g.promotePawn(newCell, g.choosePromotion())
        # TODO: remove next line
        # print(g)
        return g
    
    def save(game):
        '''Saves the log of the game into a text file'''
        from datetime import datetime
        now = datetime.now()
        filename = 'chess_%d%02d%02d%02d%02d%02d.save.txt'%(now.year, now.month, now.day, now.hour, now.minute, now.second)
        with open(filename, 'w') as file:
            for i, log in enumerate(game.log):
                file.write('%d %s-%s\n'%(i+1, game.getCell(log[0]), game.getCell(log[1])))
        #TODO: add refined notation with piece info and promotion and takes
        return filename
    
    def load(game, filename):
        '''Loads a game state from a file'''
        # TODO: manage file saving formats in accordance with save method
    
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