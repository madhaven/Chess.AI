from abc import abstractmethod, ABC
import random
from Chess import Chess

class Player(ABC):
    '''Contains implementations of a players functionality.'''

    @abstractmethod
    def chooseMove(self, game:Chess) -> list:
        pass

    @abstractmethod
    def choosePromotion(self, game:Chess) -> str:
        pass

class PlayerRandom(Player):

    def chooseMove(self, game:Chess) -> list:
        return random.choice(game.getMoves())
    
    def choosePromotion(self, game:Chess) -> str:
        return random.choice('QRBN')

class PlayerGreedy(PlayerRandom):

    def chooseMove(self, game: Chess) -> list:
        moves = game.getMoves()
        attackMoves = [
            move for move in moves
            if game.pieceAt(move[1]) != None and game.pieceAt(move[1])[0] == ('b' if game.isWhitesMove else 'w')
        ]
        if attackMoves:
            print(attackMoves)
        return random.choice(attackMoves if attackMoves else moves)
        