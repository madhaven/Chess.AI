from Chess import Chess

game = Chess()
while (game.gameOver()==False):
    try:
        print(
            '\nGame State', 'WhitesMove : '+str(game.isWhitesMove),
            'result : '+str(game.gameResult), 'Log : '+str(game.log), sep='\n'
        )
        print(game, end='')
        move = input('next move : ')
        if 'save' in move.lower(): game.save()
        else:game = game.makeMove(*move.split())
    except:
        print('An error occured. The game log has been saved to '+game.save())
input()