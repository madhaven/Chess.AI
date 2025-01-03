from Chess import Chess, Player
from Players import PlayerRandom
from random import choice

class MinimaxPlayer_00(PlayerRandom):
    '''
    Maximizes the "opportunity" of taking pieces.
    to no surprise, it doesn't prioritize takes, only the opportunity. XD
    '''

    def __init__(self, depth = 1):
        self.depth = depth
    
    def value(self, game: Chess) -> int:
        '''Provides the value of a game state by evaluating the number of takes possible.'''
        point_map = { 'P':1, 'N':3, 'B':3, 'R':5, 'Q':9 }
        attackTargets = [move[1] for move in game.getMoves() if game.isAttackMove(move[0], move[1])]
        targetPieces = [game.pieceAt(cell) for cell in attackTargets]
        points = 0
        for piece in targetPieces:
            pieceValue = point_map[piece[1]]
            if piece[0] == 'w':
                points -= pieceValue
            elif piece[0] == 'b':
                points += pieceValue
        return points

    def max_move(self, game: Chess):
        moves = game.getMoves()
        value_map = { move: self.value(game.makeMove(move[0], move[1]))
            for move in moves }
        values = value_map.values()
        best_value = max(values) if game.isWhitesMove else min(values)
        best_moves = [move for move in value_map if value_map[move] == best_value]
        return choice(best_moves)

    def chooseMove(self, game: Chess) -> list:
        bestMove = self.max_move(game)
        return bestMove
    
class MinimaxPlayer_01(MinimaxPlayer_00):
    
    def __init__(self, depth=1):
        self.depth = depth
    
    def minimax(self, game: Chess, depth=1):
        if depth == 1:
            return self.value(game)

        moves = game.getMoves()
        value_map = { move: self.minimax(game.makeMove(move[0], move[1]), depth-1) for move in moves }
        values = value_map.values()
        best_value = max(values) if game.isWhitesMove else min(values)
        return best_value
    
    def chooseMove(self, game: Chess) -> list:
        moves = game.getMoves()
        value_map = { move: self.minimax(game.makeMove(move[0], move[1])) for move in moves }
        values = value_map.values()
        best_value = max(values) if game.isWhitesMove else min(values)
        best_moves = [move for move in value_map if value_map[move] == best_value]
        best_move = choice(best_moves)
        return best_move

class MinimaxPlayer_02(MinimaxPlayer_01):
    '''
    Tries to prioritize a good board state that maximizes the POSSIBILITY of takes.
    But does not really take pieces
    '''
    def __init__(self, depth):
        self.depth = depth
    
    def value(self, game: Chess) -> int:
        '''Provides the value of a game state by evaluating the number of takes possible.'''
        point_map = { 'P':1, 'N':3, 'B':3, 'R':5, 'Q':9 }
        attackTargets = [ move[1] for move in game.getMoves() if game.isAttackMove(move[0], move[1]) ]
        targetPieces = [ game.pieceAt(cell) for cell in attackTargets ]
        maxPiece = 0
        points = 0
        for piece in targetPieces:
            pieceValue = point_map[piece[1]]
            if pieceValue > maxPiece:
                maxPiece = pieceValue
            if piece[0] == 'w':
                points -= pieceValue
            elif piece[0] == 'b':
                points += pieceValue
        return points + 10 * maxPiece

class MinimaxPlayer_03(Player):

    def __init__(self, depth):
        self.depth = depth
    
    def getName(self) -> str:
        return self.__class__.__name__ + f'({self.depth})'
    
    def gameValue(self, game: Chess) -> int:
        attackTargets = [ move[1] for move in game.getMoves() if game.isAttackMove(move[0], move[1]) ]
        targetPieces = [ game.pieceAt(cell) for cell in attackTargets ]

        # attack options
        points = sum([game.piecePoints(piece) for piece in targetPieces])

        # points for previous take
        if game.history:
            lastMove = game.history[-1]
            if 'x' in lastMove:
                piece = ("w" if game.isWhitesMove else "b") + lastMove.split('x')[1][0]
                points += (game.piecePoints(piece) * 10)
        return points

    def minimax(self, game: Chess, depth=1):
        if depth == 1: return self.gameValue(game)

        value_map = {
            move: self.minimax(game.makeMove(move[0], move[1]), depth-1)
            for move in game.getMoves()
        }
        values = value_map.values()
        best_value = max(values) if game.isWhitesMove else min(values)
        return best_value
    
    def chooseMove(self, game: Chess) -> list:
        moves = game.getMoves()
        value_map = { move: self.minimax(game.makeMove(*move)) for move in moves }
        values = value_map.values()
        best_value = max(values) if game.isWhitesMove else min(values)
        best_moves = [move for move in value_map if value_map[move] == best_value]
        best_move = choice(best_moves)
        return best_move

    def choosePromotion(self, game: Chess) -> str:
        return 'Q'