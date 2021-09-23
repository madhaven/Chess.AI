from Chess import Chess
import code

game = Chess.loadFrom(input('Drop your saved Chess game : '))
print(game)
code.interact(banner='use `game` for control', local=dict(globals(), **locals()), exitmsg='')
