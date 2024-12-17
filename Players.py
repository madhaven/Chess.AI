from Chess import *

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
            if game.isAttackMove(*move)
        ]
        if attackMoves:
            print('attack moves:', *[f'{game.notation(a)}-{game.notation(b)},' for a, b in attackMoves])
        return random.choice(attackMoves if attackMoves else moves)