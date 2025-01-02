from Chess import Chess
from pytest import skip
from unittest.mock import patch

def test_init():
    game = Chess()
    
    assert game.board == [
        ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'], #a8 - h8
        ['bP']*8, [None]*8, [None]*8, [None]*8, [None]*8, ['wP']*8,
        ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR'], #a1 - h1
    ]
    assert game.isWhitesMove
    assert game.result == None
    assert game.wPoints == 0
    assert game.bPoints == 0
    assert game.log == []
    assert game.gameString == ''
    assert game.history == []
    assert game.fiftyCounter == 0

# TODO: add strings with game actions, castling, takes, checkmates, en passant
def test_init_with_gamestring():
    game_string = 'Pd2-d4 Pd7-d5 Pe2-e4'
    game = Chess(game_string)

    assert game.board == [
        ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'], #a8 - h8
        ['bP', 'bP', 'bP', None, 'bP', 'bP', 'bP', 'bP'],
        [None]*8,
        [None, None, None, 'bP', None, None, None, None],
        [None, None, None, 'wP', 'wP', None, None, None],
        [None]*8,
        ['wP', 'wP', 'wP', None, None, 'wP', 'wP', 'wP'],
        ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR'], #a1 - h1
    ]
    assert not game.isWhitesMove
    assert game.result == 0
    assert game.wPoints == 0
    assert game.bPoints == 0
    assert game.log == [
        ((3, 6), (3, 4)),
        ((3, 1), (3, 3)),
        ((4, 6), (4, 4))
    ]
    assert game.gameString == game_string
    assert game.history == [
        'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR',
        'rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR',
        'rnbqkbnr/ppp1pppp/8/3p4/3P4/8/PPP1PPPP/RNBQKBNR'
    ]
    assert game.fiftyCounter == 0

def test_str():
    game = Chess('Pe2-e4 Pc7-c5 Bf1-c4 Ng8-f6')
    str_printed = str(game)
    assert str_printed == '''
8| r n b q k b   r |
7| p p   p p p p p |
6|           n     |
5|     p           |
4|     B   P       |
3|                 |
2| P P P P   P P P |
1| R N B Q K   N R |
   a b c d e f g h
'''

def test_eq():
    game1 = Chess()
    game2 = Chess()
    assert game1 == game2

    game1.makeMove('a2', 'a4')
    game2.makeMove('a2', 'a4')
    assert game1 == game2

def test_coords():
    for x, ch in enumerate('abcdefgh'):
        for y in range(8, 0, -1):
            assert Chess.coords(f'{ch}{y}') == (x, 8-y)

def test_notation():
    for x in range(7):
        for y in range(7):
            cell = 'abcdefgh'[x] + str(8-y)
            assert Chess.notation((x, y)) == cell

def test_piecePoints():
    assert Chess.piecePoints('bQ') == 9
    assert Chess.piecePoints('wQ') == -9
    assert Chess.piecePoints('bR') == 5
    assert Chess.piecePoints('wR') == -5
    assert Chess.piecePoints('bN') == 3
    assert Chess.piecePoints('wN') == -3
    assert Chess.piecePoints('bB') == 3
    assert Chess.piecePoints('wB') == -3
    assert Chess.piecePoints('bP') == 1
    assert Chess.piecePoints('wP') == -1

def test_checkResult():
    game = Chess()
    assert game.checkResult() == 0
    
    game.fiftyCounter = 100
    assert game.checkResult() == 6

    game.fiftyCounter = 0
    with patch('Chess.Chess.getMoves', lambda *x: []):
        with patch('Chess.Chess.isCheck', lambda *x: True):
            game.isWhitesMove = True
            assert game.checkResult() == -1
            assert game.gameString [-1] == '#'
            game.isWhitesMove = False
            assert game.checkResult() == 1
            assert game.gameString [-1] == '#'
        assert game.checkResult() == 3
    
    game.history = [game.FEN()]*2
    assert game.checkResult() == 5

    game.history = []
    game.board = [
        ['wK', None, 'bK', None, None, None, None, None],
        [None]*8, [None]*8, [None]*8,
        [None]*8, [None]*8, [None]*8, [None]*8
    ]
    assert game.checkResult() == 4

    game.board[0] = ['bK', None, 'wK', 'wB', None, None, None, None]
    assert game.checkResult() == 4
    game.board[0] = ['wK', None, 'bK', 'bB', None, None, None, None]
    assert game.checkResult() == 4
    game.board[0] = ['bK', None, 'wK', 'wN', None, None, None, None]
    assert game.checkResult() == 4
    game.board[0] = ['wK', None, 'bK', 'bN', None, None, None, None]
    assert game.checkResult() == 4
    game.board[0] = ['wK', None, 'bK', 'bB', None, 'wB', None, None]
    assert game.checkResult() == 4

    # game.board[0] = ['wK', None, 'bK', 'wN', None, None, None, None]
    # assert game.checkResult() == 0

def test_isCheck():
    def flip_board(game: Chess):
        '''flips black pieces to white and white to black'''
        for x in range(8):
            for y in range(8):
                if not game.board[x][y]: continue
                side = game.board[x][y][0]
                flip = 'w' if side == 'b' else 'b'
                game.board[x][y] = f'{flip}{game.board[x][y][1]}'
        game.isWhitesMove = not game.isWhitesMove
    
    game = Chess()
    game.board = [[None]*8]*8
    game.board[0] = ['wK', None, None, None, None, None, 'bR', 'bK']
    assert game.isCheck()
    flip_board(game)
    assert game.isCheck()

    # TODO: add all other pieces
    # game.board[0] = ['wK'] + [None]*6 + ['bK']
    # game.board[1] = ['bR'] + [None]*7
    # assert game.isCheck()
    # flip_board(game)
    # assert game.isCheck()

def test_pieceAt():
    game = Chess()
    assert game.pieceAt((0, 0)) == 'bR'
    assert game.pieceAt('a8') == 'bR'
    assert game.pieceAt([7, 7]) == 'wR'
    assert game.pieceAt('h1') == 'wR'

def test_getMoves():
    game = Chess()
    moves = []
    for x in range(8):
        moves.append(((x, 6), (x, 5)))
        moves.append(((x, 6), (x, 4)))
    moves.extend([
        ((1, 7), (0, 5)),
        ((1, 7), (2, 5)),
        ((6, 7), (5, 5)),
        ((6, 7), (7, 5))
    ])
    assert game.getMoves() == moves

def test_legalMoves():
    game = Chess()
    assert game.legalMoves('a1') == [(0, 0), (1, 7), (0, 1), (2, 7), (0, 2), (3, 7), (0, 3), (4, 7), (0, 4), (5, 7), (0, 5), (6, 7), (0, 6), (7, 7)]

    assert game.legalMoves('b1') == [(0, 5), (2, 5), (3, 6)]
    # TODO: so many move functions ... refine logic

def test_makeMove():
    game = Chess()
    game = game.makeMove('a2', 'a4')
    game2 = Chess('Pa2-a4')
    assert game == game2
    # TODO add other cases