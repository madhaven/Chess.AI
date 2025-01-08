from copy import deepcopy
from datetime import datetime
from abc import ABC, abstractmethod
import random
from os import sep

class Chess:
    '''Contains all logic for a chess game'''
    def __init__(self, gameString:str=None):
        """intializes the board and sets the state of the board."""
        if not gameString:
            self.board = [
                ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'], #a8 - h8
                ['bP']*8, [None]*8, [None]*8, [None]*8, [None]*8, ['wP']*8,
                ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR'], #a1 - h1
            ]
            self.isWhitesMove = True
            self.result = None
            self.wPoints = 0
            self.bPoints = 0
            self.log = []
            self.gameString:str = ''
            self.history:list[str] = []
            self.fiftyCounter = 0
        else:
            game = Chess()
            for i, move in enumerate(gameString.split()):
                if move == 'O-O-O': a, b = (4, 7 if i%2==0 else 0), (2, 7 if i%2==0 else 0)
                elif move == 'O-O': a, b = (4, 7 if i%2==0 else 0), (6, 7 if i%2==0 else 0)
                else:
                    a, b = move.split('x' if 'x' in move else '-')
                    promoteToPiece = b.split('=')[1] if '=' in b else None
                    a = a[1:3] if a[0].isupper() else a[:2]
                    b = b[1:3] if b[0].isupper() else b[:2]
                    game = game.makeMove(a, b, promoteTo=promoteToPiece)
            self.board = game.board
            self.isWhitesMove = game.isWhitesMove
            self.result = game.result
            self.wPoints = game.wPoints
            self.bPoints = game.bPoints
            self.log = game.log
            self.gameString:str = game.gameString
            self.history = game.history
            self.fiftyCounter = game.fiftyCounter
    
    def __str__(game) -> str:
        '''prints the board on console'''
        string = '\n'
        for y, row in enumerate(game.board):
            string += '%d| '%(8-y)
            for cell in row:
                if not cell: string += '  '
                elif cell[0]=='b': string += cell[1].lower()+' '
                elif cell[0]=='w': string += cell[1].upper()+' '
            string += '|\n'
        string += '   a b c d e f g h\n'
        return string
    
    def __eq__(game, game2: "Chess") -> bool:
        if game.gameString != game2.gameString:
            return False
        return True

    @staticmethod
    def coords(cell: str) -> tuple:
        '''Accepts a string Chess-cell location and returns x-y tuple indices on the board'''
        return (ord(cell[0].lower())-97, 8-int(cell[1]))
    
    @staticmethod
    def notation(cell) -> str:
        '''Accepts a duplet cell, array location and returns a string notation of the cell'''
        return 'abcdefgh'[cell[0]]+str(8-cell[1])
    
    @staticmethod
    def piecePoints(piece: str):
        '''returns the points for a piece.\n
        White pieces give negative values.'''
        value = { 'Q':9, 'R':5, 'N':3, 'B':3, 'P':1, 'K':0 }[piece[1]]
        if piece[0] == 'w': value *= -1
        return value
    
    def FEN(game) -> str:
        '''Returns a Forsyth-Edwards Notation (FEN) of the board without game information.
        Saving boards as strings is expected to speed up history checks when compared to arrays.'''
        fen = ''
        for row in game.board:
            emptyCells = 0
            for cell in row:
                if not cell: emptyCells += 1
                else: 
                    if emptyCells:
                        fen += str(emptyCells)
                        emptyCells = 0
                    fen += cell[1].upper() if cell[0]=='w' else cell[1].lower()
            if emptyCells: fen += str(emptyCells)
            fen += '/'
        return fen[:-1]

    def checkResult(game) -> int:
        """
        checks for a result from the board.
        0  in progress
        1  white won
        -1 black won
        2  quit
        3  stalemate
        4  draw by insufficient material
        5  draw by three-fold repetition
        6  draw by fifty-move rule
        """

        if game.fiftyCounter >= 100:
            game.result = 6
        elif not game.getMoves():
            if game.isCheck():
                if game.isWhitesMove: game.result = -1
                else: game.result = 1
                game.gameString += '#'
            else: game.result = 3
        elif game.history.count(game.FEN())>=2:
            game.result = 5
        else:
            bp, wp = [], []
            for y in range(8):
                for x in range(8):
                    piece = game.pieceAt((x, y))
                    if not piece or piece[1]=='K': continue
                    if piece[0]=='b':
                        bp.append(piece[1])
                        if piece[1]=='B': bbcol = (x+y)%2
                    elif piece[0]=='w':
                        wp.append(piece[1])
                        if piece[1]=='B': wbcol = (x+y)%2
            # TODO: make sure no takes are possible
            # Currently even if king can cut the last bishop, game is draw
            if bp==wp==[] or \
                (bp==[] and wp==['B']) or (bp==['B'] and wp==[]) or \
                (bp==[] and wp==['N']) or (bp==['N'] and wp==[]) or \
                (bp==wp==['B'] and bbcol==wbcol):
                game.result = 4
            else:
                game.result = 0

        return game.result

    def isCheck(game, check_side=None) -> bool:
        '''Returns a boolean specifying if the current player is in check or not.
        If check_side is set to w or b, checking is made for white or black respectively.'''
        if not check_side: check_side = 'w' if game.isWhitesMove else 'b'
        for y, row in enumerate(game.board):
            for x, cell in enumerate(row):
                if game.pieceAt((x, y)) == check_side+'K':
                    king=(x, y)
                    break
            else: continue
            break
        for checkPiece in ['P', 'RQ', 'BQ', 'N', 'K']:
            for coord in game.checkableMoves(king, check_side+checkPiece[0]):
                # places a piece in kings cell and finds same enemy pieces in sight
                piece = game.pieceAt(coord)
                if piece and piece[0]!=check_side and piece[1] in checkPiece:
                    return True
        return False

    def pieceAt(game, cell: str|tuple[int, int]):
        x, y = game.coords(cell) if isinstance(cell, str) else cell
        return game.board[y][x]

    def getMoves(game, currentSide=None) -> list:
        '''Returns a list of possible moves (pairs of xy coordinate pairs)'''
        if not currentSide: currentSide = 'w' if game.isWhitesMove else 'b'
        pieces = [
            (x, y) for y, row in enumerate(game.board)
            for x, cell in enumerate(row)
            if cell != None and cell[0] == currentSide]
        return [
            (piece, move) for piece in pieces
            for move in game.movesOfCell(piece)]
    
    def legalMoves(self, cell, piece=None) -> list[tuple[int, int]]:
        '''Returns a list of legal moves for a piece in the cell.
        if piece (PRNBQK) is explicitly specified the rules of that piece would apply.
        This method does not consider the state of the game, only the position of the piece.
        Intended to be used when making PreMoves.'''

        x, y = self.coords(cell) if isinstance(cell, str) else cell
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
            ops = self.legalMoves((x, y), current_side+'B') + self.legalMoves((x, y), current_side+'R')

        elif piece[1] == 'K':
            ops = [
                (dx, dy) for dy in range(y-1, y+2)
                for dx in range(x-1, x+2)
                if 0<=dy<8 and 0<=dx<8
            ]
            ops.remove((x, y))
        
        return ops
    
    def checkableMoves(self, cell, piece=None) -> list:
        '''Returns a list of squares eyed/targetted by a piece in the cell, 
        This method refines moves from legalMoves by ensuring no pieces block the way.
        This method Does not however check if the move is completely possible.'''
        
        x, y = self.coords(cell) if isinstance(cell, str) else cell
        if not piece:
            piece = self.board[y][x]
            if not piece: return []
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
            ops = self.checkableMoves((x, y), current_side+'B') +\
                self.checkableMoves((x, y), current_side+'R')

        elif piece[1] == 'K':
            ops = moves # [ op for op in moves if op[0]-x in (-1, 0, 1) ]
            
        return ops
    
    def movesOfCell(game, cell, piece=None) -> list:
        '''The go to method to fetch the moves a cell can make\n
        Fetchs the available moves, adds other checkable moves for pawns, castling moves and makes sure the move doesn't result in a check.'''
        x, y = game.coords(cell) if isinstance(cell, str) else cell
        if not piece:
            piece = game.pieceAt((x, y))
            if not piece: return []
        
        current_side = piece[0]
        moves = []
        
        if piece[1]=='P':
            for op in game.legalMoves((x, y), piece):
                if op[0]-x == 0: # straight move
                    if not game.pieceAt(op): # empty square
                        if op[1]-y in (1, -1):
                            moves.append(op) # one step
                        elif op[1]-y in (2, -2) and not game.pieceAt((op[0], (op[1]+y)//2)):
                            moves.append(op) # two steps and empty path
                else: # sidemove
                    if game.pieceAt(op) and game.pieceAt(op)[0] != current_side: #takes
                        moves.append(op)
                    elif len(game.log)>0 and y==(3 if current_side=='w' else 4) and\
                        op[1]==(game.log[-1][0][1]+game.log[-1][1][1])/2 and\
                        game.log[-1][0][0]==game.log[-1][1][0]==op[0]: # en passant
                            moves.append(op)
        else: moves = game.checkableMoves((x, y), piece)

        # add castling moves
        if piece[1]=='K':
            kingMoved = game.hasMoved((4, 0)) if current_side=='b' else game.hasMoved((4, 7))
            if not kingMoved and not game.isCheck():
                if not game.hasMoved((7, y)) and \
                game.pieceAt((5, y)) == game.pieceAt((6, y)) == None and \
                not game.makeMove((4, y), (5, y), _testMove=True).isCheck(current_side) :
                    moves.append((6, y))
                if not game.hasMoved((0, y)) and \
                game.pieceAt((1, y)) == game.pieceAt((2, y)) == game.pieceAt((3, y)) == None and \
                not game.makeMove((4, y), (3, y), _testMove=True).isCheck(current_side) :
                    moves.append((2, y))

        # ensure proposed move doesn't have a friendly piece on it and don't result in check
        finalMoves = [ 
            move for move in moves 
            if (not game.pieceAt(move) or game.pieceAt(move)[0] != current_side)
            and not game.makeMove((x,y), move, _testMove=True).isCheck(current_side)
        ]
        return finalMoves
    
    def hasMoved(game, cell) -> bool:
        '''Returns a boolean that tells wether or not a move has been made from the cell during the game'''
        if isinstance(cell, str): cell = game.coords(cell)
        for move in game.log:
            if list(move[0]) == list(cell):
                return True
        return False
    
    def makeMove(game, oldCell, newCell, promoteTo:str='Q', _testMove=False) -> "Chess":
        '''Returns an instance of the board after having made the move\n
        `_testMove` is intended for blocking user action in case of possible pawn promotions'''
        if isinstance(oldCell, str): oldCell = game.coords(oldCell)
        if isinstance(newCell, str): newCell = game.coords(newCell)
        
        if not game.pieceAt(oldCell) \
        or (game.pieceAt(oldCell)[0]=='w' and not game.isWhitesMove) \
        or (game.pieceAt(oldCell)[0]=='b' and game.isWhitesMove):
            return game

        current_side = game.pieceAt(oldCell)[0]
        g = deepcopy(game)

        # the move
        g.board[newCell[1]][newCell[0]] = g.board[oldCell[1]][oldCell[0]]
        g.board[oldCell[1]][oldCell[0]] = None
        g.isWhitesMove = not g.isWhitesMove
        g.history.append(game.FEN())

        if game.pieceAt(oldCell)[1]=='P': g.fiftyCounter = 0
        else: g.fiftyCounter += 1

        if game.pieceAt(newCell):
            if game.pieceAt(newCell)[0] != current_side:
                # piece acquired
                g.fiftyCounter = 0
                g.gameString += ' '+game.pieceAt(oldCell)[1]+game.notation(oldCell)+'x'+game.pieceAt(newCell)[1]+game.notation(newCell)
                # TODO: add points for piece acquired
            else: # cannot move to own piece's square
                return game

        #en passant
        elif len(game.log)>0 and oldCell[1]==(3 if current_side=='w' else 4) and\
            newCell[1]==(game.log[-1][0][1]+game.log[-1][1][1])/2 and newCell[0]-oldCell[0]!=0 and\
            game.log[-1][0][0]==game.log[-1][1][0]==newCell[0]:
            g.fiftyCounter = 0
            g.gameString += ' '+game.pieceAt(oldCell)[1]+game.notation(oldCell)+'xP'+game.notation(newCell)
            g.board[oldCell[1]][newCell[0]] = None
            # TODO: add game points for en passant
        
        #castling
        elif game.pieceAt(oldCell)[1]=='K' and not game.hasMoved(oldCell):
            if oldCell[0]-newCell[0] == 2: #queenside
                if not game.hasMoved((0, oldCell[1])):
                    g.board[oldCell[1]][3]=current_side+'R'
                    g.board[oldCell[1]][0]=None
                    g.gameString += ' '+'O-O-O'
            elif oldCell[0]-newCell[0] == -2: #kingside
                if not game.hasMoved((7, oldCell[1])):
                    g.board[oldCell[1]][5]=current_side+'R'
                    g.board[oldCell[1]][7]=None
                    g.gameString += ' '+'O-O'

        else: g.gameString += \
            (' ' if g.gameString else '')+game.pieceAt(oldCell)[1]+game.notation(oldCell)+'-'+game.notation(newCell)
        
        #pawn promotion # TODO: None check is required to handle an unknown bug that results in g.board[.][.] to be None
        if g.board[newCell[1]][newCell[0]] != None\
                and g.board[newCell[1]][newCell[0]][1]=='P' \
                and newCell[1]%7 == 0:
            newPiece = 'Q' if _testMove else promoteTo
            if newPiece in 'RNBQ':
                g.fiftyCounter = 0
                g.board[newCell[1]][newCell[0]] = current_side + newPiece
                g.gameString += '='+newPiece
            else: return game

        #game states
        g.log.append((oldCell, newCell))
        if not _testMove: g.checkResult()
        
        return g

    def isAttackMove(game, oldCell, newCell):
        # TODO add en passant
        if game.pieceAt(newCell) == None: return False
        return game.pieceAt(oldCell)[0] != game.pieceAt(newCell)[0]

    def save(game, filename:str=None, comments=None):
        '''Saves the log of the game into a text file'''
        
        if not filename:
            now = datetime.now()
            filename = sep.join(['assets', 'sampleGames',
                'chess_%d%02d%02d%02d%02d%02d.save.txt'%(now.year, now.month, now.day, now.hour, now.minute, now.second)])
        
        with open(filename, 'w') as file:
            file.write(game.gameString + '\n')
            if comments:
                file.write(comments + '\n')
        return filename
    
    @staticmethod
    def loadFrom(filename, promotion=None) -> "Chess":
        '''Loads a game state from a .save version file.'''
        lines = open(filename, 'r').readlines()
        game = Chess(gameString=lines[0])
        print('game initialized', game)
        return game

class Player(ABC):
    '''Contains implementations of a players functionality.'''

    def getName(self) -> str:
        '''
        return a string representing the instance.\n
        This will be used to identify the player in the logs
        '''
        return self.__class__.__name__

    @abstractmethod
    def chooseMove(self, game:Chess) -> list:
        pass

    @abstractmethod
    def choosePromotion(self, game:Chess) -> str:
        pass
