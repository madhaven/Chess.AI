from Chess import Chess
import code

file = input('Drop your saved Chess game if any : ')
game = Chess.loadFrom(file) if file else Chess()
print(game)
code.interact(banner='use `game` for control', local=dict(globals(), **locals()), exitmsg='')
