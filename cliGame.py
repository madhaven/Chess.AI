from Chess import Chess

game = Chess()
# try:
while (game.gameOver()==False):
    print(
        '\nGame State', 'WhitesMove : '+str(game.isWhitesMove),
        'result : '+str(game.gameResult), 'Log : '+str(game.log), sep='\n'
    )
    print(game, end='')
    move = input('next move : ')
    if move=='save': game.save()
    else:game = game.makeMove(*move.split())
# except:
#     print('An error occured. The game log has been saved to '+game.save())