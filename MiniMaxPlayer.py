from Chess import Chess, Player
from Players import PlayerRandom
from random import choice

class MinimaxPlayers:
    
    @staticmethod
    def latest():
        return [
            MinimaxPlayer_00
            , MinimaxPlayer_01
            , MinimaxPlayer_02
            , MinimaxPlayer_03
        ][-1]

class MinimaxPlayer_00(PlayerRandom):
    '''
    Maximizes the "opportunity" of taking pieces.
    to no surprise, it doesn't prioritize takes, only the opportunity. XD
    '''

    def __init__(self, depth = 1):
        self.depth = depth
        self.point_map = { 'P':1, 'N':3, 'B':3, 'R':5, 'Q':9 }
    
    def value(self, game: Chess) -> int:
        '''Provides the value of a game state by evaluating the number of takes possible.'''
        attackTargets = [move[1] for move in game.getMoves() if game.isAttackMove(move[0], move[1])]
        targetPieces = [game.pieceAt(cell) for cell in attackTargets]
        points = 0
        for piece in targetPieces:
            pieceValue = self.point_map[piece[1]]
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
    '''board evaluation is a bit greedy as it sacrificed Queen for no advantage, quite slow'''

    def __init__(self, depth):
        self.depth = depth
    
    def getName(self) -> str:
        return self.__class__.__name__ + f'(depth:{self.depth})'
    
    def gameValue(self, game: Chess) -> int:
        attackTargets = [ move[1] for move in game.getMoves() if game.isAttackMove(*move) ]
        targetPieces = [ game.pieceAt(cell) for cell in attackTargets ]

        # attack options
        points = sum([game.piecePoints(piece) for piece in targetPieces]) or 0

        # points for previous take
        if game.history:
            lastMove = game.gameString.split()[-1]
            if 'x' in lastMove:
                piece = ("w" if game.isWhitesMove else "b") + lastMove.split('x')[1][0]
                points += (game.piecePoints(piece) * 10)
        return points

    def minimax(self, game: Chess, depth: int) -> int:
        if depth == 0 or game.checkResult() != 0:
            return self.gameValue(game)
        
        value = 0
        if not game.isWhitesMove:
            for move in game.getMoves():
                value = max(value, self.minimax(game.makeMove(*move), depth-1))
            return value
        else:
            for move in game.getMoves():
                value = min(value, self.minimax(game.makeMove(*move), depth-1))
            return value
    
    def chooseMove(self, game: Chess) -> list:
        moves = game.getMoves()
        value_map = dict() # { move: self.minimax(game.makeMove(*move), depth=self.depth) for move in moves }
        n = len(moves)
        for i, move in enumerate(moves):
            print(f'thinking {(i+1)*100//n}%')
            value_map[move] = self.minimax(game.makeMove(*move), depth=self.depth)
        values = set(value_map.values())
        best_value = max(values) if game.isWhitesMove else min(values)
        best_moves = [move for move in value_map if value_map[move] == best_value]
        best_move = choice(best_moves)
        return best_move

    def choosePromotion(self, game: Chess) -> str:
        return 'Q'

class MinimaxPlayer_04(MinimaxPlayer_03):
    '''
    trying to implement an alpha-beta pruning this time: performance improved
    also added a value estimation that's unbiased on which side is playing.
    Not afraid of getting taken
    '''

    def __init__(self, depth):
        self.depth = depth

    def gameValue(self, game: Chess) -> int:
        points = 0

        # checkmate score
        result = game.checkResult()
        if result == 1:
            return 1e6
        elif result == -1:
            return -1e6

        # opportunity score        
        attackTargets = [ move[1] for move in game.getMoves('w' if game.isWhitesMove else 'b') if game.isAttackMove(*move) ]
        piecesForTakes = [ game.pieceAt(cell) for cell in attackTargets ]
        points += sum([game.piecePoints(piece) for piece in piecesForTakes]) or 0

        # points for previous take
        if game.history:
            lastMove = game.gameString.split()[-1]
            if 'x' in lastMove:
                piece = ("w" if game.isWhitesMove else "b") + lastMove.split('x')[1][0]
                points += (game.piecePoints(piece) * 2)
        
        return points
    
    def minimax(self, game: Chess, depth: int, alphabeta: list[int|float] = [float('-inf'), float('inf')]) -> int:
        if depth == 0 or game.checkResult() != 0:
            value = self.gameValue(game)
            return value
        
        if game.isWhitesMove:
            value = float('-inf') 
            for move in game.getMoves():
                newGame = game.makeMove(*move)
                value = max(value, self.minimax(newGame, depth-1, alphabeta))
                alphabeta[0] = max(alphabeta[0], value)
                if alphabeta[0] >= alphabeta[1]:
                    break
        else:
            value = float('inf')
            for move in game.getMoves():
                newGame = game.makeMove(*move)
                value = min(value, self.minimax(newGame, depth-1, alphabeta))
                alphabeta[1] = min(alphabeta[1], value)
                if alphabeta[0] >= alphabeta[1]:
                    break
        return value
    
    def chooseMove(self, game: Chess) -> list:
        moves = game.getMoves()
        n = len(moves)
        value_map: dict[list[list[int]], int] = dict()
        for i, move in enumerate(moves):
            print(f'thinking {(i+1)*100//n}%')
            newGame = game.makeMove(*move)
            value_map[move] = self.minimax(newGame, self.depth-1)
        values = set(value_map.values())
        best_value = max(values) if game.isWhitesMove else min(values)
        best_moves = [move for move in value_map if value_map[move] == best_value]
        print(f'{min(values)}-{max(values)}:{best_value}',
            *[f'{game.notation(move[0])}-{game.notation(move[1])}' for move in best_moves])
        best_move = choice(best_moves)
        return best_move