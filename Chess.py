from copy import deepcopy

class Player:
    '''Contains implementations of a players functionality.'''
    def __init__(self, White=True):
        pass

    def chooseMove(self, game):
        '''Select a move from the available moves in game'''
        pass

    def choosePromotion(self, game):
        '''Returns a char (RNBQ) indicating which piece to promote a pawn to'''
        pass
    

class Chess:
    '''Contains all logic for a chess game'''
    def __init__(self, promotion=None, board=None, log=[], isWhitesMove=True, gameResult=None, wPoints=0, bPoints=0):
        """intializes the board and sets the state of the board.

        The choosePiece argument expects a function that returns a character in (Q, R, B, N).
        This function will be used when a pawn is to be promoted. If choosePiece defaults to None,
        the pawn will be promoted to Queen."""
        self.board = board if board else {
            (0, 0):'bR', (7, 0):'bR', (0, 7):'wR', (7, 7):'wR',
            (2, 0):'bB', (5, 0):'bB', (2, 7):'wB', (5, 7):'wB',
            (1, 0):'bN', (6, 0):'bN', (1, 7):'wN', (6, 7):'wN',
            (3, 0):'bQ', (4, 0):'bK', (3, 7):'wQ', (4, 7):'wK',
            (0, 1):'bP', (0, 6):'wP', (1, 1):'bP', (1, 6):'wP',
            (2, 1):'bP', (2, 6):'wP', (3, 1):'bP', (3, 6):'wP',
            (4, 1):'bP', (4, 6):'wP', (5, 1):'bP', (5, 6):'wP',
            (6, 1):'bP', (6, 6):'wP', (7, 1):'bP', (7, 6):'wP',
        }
        self.isWhitesMove = isWhitesMove
        self.log = log
        self.node_list = []
        self.result = gameResult
        self.wPoints = wPoints
        self.bPoints = bPoints
        self.choosePiece = promotion if promotion else lambda:'Q'
        # TODO : add logic to create game string from all moves
        # TODO : add static method to initialize game from such a game log
    
    def __str__(game):
        '''prints the board on console'''
        string = '\n'
        for y in range(8):
            string += '%d| '%(8-y)
            for x in range(8):
                if (x,y) not in game.board: string += '  '
                elif game.board[x,y][0]=='b': string += game.board[x,y][1].lower()+' '
                elif game.board[x,y][0]=='w': string += game.board[x,y][1].upper()+' '
            string += '|\n'
        string += '   a b c d e f g h\n'
        return string
    
    def __eq__(game1, game2):
        '''Checks if two boards are at the same state. Used for 3-move repetition checks'''
        return game1.board==game2.board
    
    def _coords_(game, string):
        '''Accepts a string Chess-cell location and returns x-y tuple indices on the board'''
        return (ord(string[0].lower())-97, 8-int(string[1]))
    
    def _notation_(game, cell):
        '''Accepts a duplet cell, array location and returns a string notation of the cell'''
        return 'abcdefgh'[cell[0]]+str(8-cell[1])
    
    def checkResult(game):
        """
        checks for a result from the board.
        1  white won
        -1 black won
        2  quit
        3  stalemate
        4  draw by insufficient material
        5  three fold repetition
        """
        if not game.getMoves():
            if game.isCheck():
                if game.isWhitesMove: game.result = -1
                else: game.result = 1
            else: game.result = 3
        else:
            bp = [p for p in game.board.values() if p[0]=='b' and p[1]!='K']
            wp = [p for p in game.board.values() if p[0]=='w' and p[1]!='K']
            bbcol = [(x+y)%2 for x, y in game.board if game.board[x,y]=='bB'][0]
            wbcol = [(x+y)%2 for x, y in game.board if game.board[x,y]=='wB'][0]
            if bp==wp==[] or \
                (bp==[] and wp==['B']) or (bp==['B'] and wp==[]) or \
                (bp==[] and wp==['N']) or (bp==['N'] and wp==[]) or \
                (bp==wp==['B'] and bbcol==wbcol):
                game.result = 4
            elif game.node_list.count(game) >= 2:
                game.result = 5
            else:
                game.result = None

        return game.result

    def isCheck(game, check_side=None):
        '''Returns a boolean specifying if the current player is in check or not.
        If check_side is set to w or b, checking is made for white or black respectively.'''
        # TODO: add parameter to check. so self moves don't need to brute force through options
        if not check_side: check_side = 'w' if game.isWhitesMove else 'b'
        for y in range(8):
            for x in range(8):
                if (x,y) in game.board and game.board[x,y]==check_side+'K':
                    king=(x, y)
                    break
            else: continue
            break
        for checkPiece in ['P', 'RQ', 'BQ', 'N', 'K']:
            for coord in game.checkableMoves(king, check_side+checkPiece[0]):
                #essentially places a piece in kings cell and finds same enemy pieces in sight
                if (coord[0], coord[1]) in game.board:
                    piece = game.board[coord[0],coord[1]]
                    if piece[0]!=check_side and piece[1] in checkPiece:
                        return True
        return False

    def getMoves(game, current_side=None):
        '''Returns a list of possible moves (pairs of xy coordinate pairs)'''
        if not current_side: current_side = 'w' if game.isWhitesMove else 'b'
        return [
            (piece, move) for piece in game.board
            for move in game.movesOf(piece)]
    
    def legalMoves(self, cell, piece=None):
        '''Returns a list of legal moves for a piece in the cell.
        if piece (PRNBQK) is explicitly specified the rules of that piece would apply.
        This method does not consider the state of the game, only the position of the piece.
        Intended to be used when making PreMoves.'''
        if type(cell)==str: x, y = self._coords_(cell)
        else: x, y = cell[0], cell[1]
        if not piece:
            if (x, y) not in self.board: return []
            else: piece = self.board[x,y]
        current_side = piece[0]
        ops = []

        if piece[1] == 'P':
            if current_side=='w' and y>0: d=-1
            elif current_side=='b' and y<7: d=1
            else: ops = []
            
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
    
    def checkableMoves(self, cell, piece=None):
        '''Returns a list of squares eyed/targetted by a piece in the cell, 
        This method simply refines the moves from legalMoves according to the game.
        This method Does not however check if the move is completely possible.'''
        
        if type(cell)==str: x, y = self._coords_(cell)
        else: x, y = cell[0], cell[1]
        if not piece:
            if (x,y) not in self.board: return []
            else: piece = self.board[x,y]
        current_side = piece[0]
        ops, moves = [], self.legalMoves((x, y), piece)

        if piece[1] == 'P':
            for op in moves:
                if op[0]-x in (1, -1): #sideways move
                    ops.append(op)

        elif piece[1] == 'R':
            for d in range(x+1, 8):
                ops.append((d, y))
                if (d,y) in self.board: break
            for d in range(x-1, -1, -1):
                ops.append((d, y))
                if (d,y) in self.board: break
            for d in range(y+1, 8):
                ops.append((x, d))
                if (x,d) in self.board: break
            for d in range(y-1, -1, -1):
                ops.append((x, d))
                if (x,d) in self.board: break

        elif piece[1] == 'N':
            ops = moves

        elif piece[1] == 'B':
            for d in range(1, min(8-x, 8-y)):
                ops.append((x+d, y+d))
                if (x+d, y+d) in self.board: break
            for d in range(1, min(8-x, y+1)):
                ops.append((x+d, y-d))
                if (x+d, y-d) in self.board: break
            for d in range(1, min(x+1, y+1)):
                ops.append((x-d, y-d))
                if (x-d, y-d) in self.board: break
            for d in range(1, min(x+1, 8-y)):
                ops.append((x-d, y+d))
                if (x-d, y+d) in self.board: break

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
        if type(cell)==str: x, y = game._coords_(cell)
        else: x, y = cell[0], cell[1]
        if not piece:
            if (x,y) not in game.board: return []
            else: piece = game.board[x,y]
        
        current_side = piece[0]
        moves = []
        
        if piece[1]=='P':
            for op in game.legalMoves((x, y), piece):
                if op[0]-x == 0: # straight move
                    if (op[0], op[1]) not in game.board: # empty square
                        if op[1]-y in (1, -1):
                            moves.append(op) # one step
                        elif op[1]-y in (2, -2) and (op[0], (op[1]+y)//2) not in game.board:
                            moves.append(op) # two steps and empty path
                else: # sidemove
                    if (op[0],op[1]) in game.board and game.board[op[0],op[1]][0]!=current_side: #takes
                        ('takes', game.board[x,y], game.board[op[0],op[1]])
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
                (5,y) not in game.board and (6,y) not in game.board==None and \
                not game.makeMove((4, y), (5, y), True).isCheck(current_side) :
                    moves.append((6, y))
                if not game.hasMoved((0, y)) and \
                (1,y) not in game.board and (2,y) not in game.board and (3,y) not in game.board and \
                not game.makeMove((4, y), (3, y), True).isCheck(current_side) :
                    moves.append((2, y))

        # ensure proposed move doesn't have a friendly piece on it and don't result in check
        finalMoves = [ 
            move for move in moves 
            if ((move[0],move[1]) not in game.board or game.board[move[0],move[1]][0]!=current_side)
            and not game.makeMove((x,y), move, True).isCheck(current_side)
        ]
        return finalMoves
    
    def hasMoved(game, cell):
        '''Returns a boolean that tells wether or not a move has been made from the cell during the game'''
        if type(cell)==str: x, y = game._coords_(cell)
        else: x, y = cell[0], cell[1]
        for move in game.log:
            if list(move[0]) == list((x, y)):
                return True
        return False
    
    def makeMove(game, oldCell, newCell, testMove=False):
        '''Returns an instance of the board after having made the move
        testMove is intended for blocking user action in case of possible pawn promotions'''
        if type(oldCell) == str: oldCell = game._coords_(oldCell)
        if type(newCell) == str: newCell = game._coords_(newCell)
        
        if (oldCell[0],oldCell[1]) not in game.board \
        or (game.board[oldCell[0],oldCell[1]][0]=='w' and not game.isWhitesMove) \
        or (game.board[oldCell[0],oldCell[1]][0]=='b' and game.isWhitesMove):
            return game

        current_side = game.board[oldCell[0],oldCell[1]][0]
        if (newCell[0],newCell[1]) in game.board:
            if game.board[newCell[0],newCell[1]][0]!=current_side:
                pass # TODO: add points for piece acquired
            else: # cannot move to own piece's square
                return game

        g = deepcopy(game)

        #en passant
        if len(game.log)>0 and oldCell[1]==(3 if current_side=='w' else 4) and\
            newCell[1]==(game.log[-1][0][1]+game.log[-1][1][1])/2 and newCell[0]-oldCell[0]!=0 and\
            game.log[-1][0][0]==game.log[-1][1][0]==newCell[0]:
            # print('enpessant acquired ', g.notation((newCell[0], oldCell[1])), g.board[newCell[0]][oldCell[1]])
            g.board.pop((oldCell[0],newCell[1]))
            # TODO: add game points for en passant
        
        #castling
        elif g.board[oldCell[0],oldCell[1]][1]=='K' and not g.hasMoved(oldCell):
            if oldCell[0]-newCell[0] == 2: #queenside
                if not g.hasMoved((0, oldCell[1])):
                    g.board[3, oldCell[1]]=current_side+'R'
                    g.board.pop((0, oldCell[1]))
            elif oldCell[0]-newCell[0] == -2: #kingside
                if not g.hasMoved((7, oldCell[1])):
                    g.board[5, oldCell[1]]=current_side+'R'
                    g.board.pop((7, oldCell[1]))

        # the move
        g.board[newCell[0], newCell[1]] = g.board[oldCell[0],oldCell[1]]
        g.board.pop((oldCell[0], oldCell[1]))
        g.isWhitesMove = not g.isWhitesMove
        g.node_list.append(game)

        #pawn promotion
        if g.board[newCell[0],newCell[1]][1]=='P' and newCell[1] in (0, 7):
            newPiece = 'Q' if testMove else g.choosePiece()
            if newPiece in 'RNBQ':
                g.board[newCell[0],newCell[1]] = current_side + newPiece
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
                file.write('%d. %s-%s\n'%(i+1, game._notation_(log[0]), game._notation_(log[1])))
        #TODO: add refined notation with piece info and promotion and takes
        return filename
    
    @staticmethod
    def loadFrom(filename):
        '''Loads a game state from a file. If printMoves is True, each step will be printed to console'''
        game=Chess()
        for move in [line.split()[1].split('-') for line in open(filename, 'r').readlines()]:
            game = game.makeMove(move[0], move[1])
        return game