from Chess import Chess

def testFile(filepath):
    import code
    from os import sep
    game = Chess()
    # testRook()
    # testBishop()
    # testEnPassant()

    for move in [line.split()[1].split('-') for line in open(filepath, 'r').readlines()]:
        game = game.makeMove(move[0], move[1])
    print(game)
    code.interact(banner='', local=dict(globals(), **locals()), exitmsg='')

# testFile('castlingCheckCheck.txt')
# testFile('castlingCheck.txt')
# testFile('gameEnd.txt')
# testFile('CheckMate.txt')
testFile(input('Drop your saved Chess game : '))
