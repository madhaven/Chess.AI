from Chess import Chess

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