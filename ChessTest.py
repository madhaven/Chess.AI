# from Chess import Chess
from copy import deepcopy

class Test():
    def __init__(self):
        try: from Chess import Chess
        except: print('Unable to import Chess from Chess')
        try: self.game = Chess()
        except: print('Unable to initialize Game')

        tests = [method for method in dir(Test) if not method.startswith('__')]
        for i, test in enumerate(tests):
            print('TEST', i, test)
            exec('self.'+test+'()')


def printgrid(g):
    for row in g:
        print('<', end='')
        for cell in row:
            if cell==True: print('#', end='')
            elif cell==False: print(' ', end='')
        print('>')

def Knightmoves(grid, x, y):
    g=deepcopy(grid)
    for dy in range(y-2, y+3):
        for dx in range(x-2, x+3):
            print('cell', dx, dy,':', end='')
            if 0<=dx<8 and 0<=dy<8 and dx!=x and dy!=y and abs(dx-x)!=abs(dy-y):
                g[dy][dx]=True
    return g

def BishopMoves(grid, x, y):
    g = deepcopy(grid)
    print('Bishop at', x, y)
    for k in range(0, 8):
        if 0<=y-(x-k)<8:
            print('cell', k, '%d-(%d-%d) ='%(y, x, k),y-(x-k))
            g[k][y-(x-k)] = True
        if 0<=y+(x-k)<8:
            print('cell', k, '%d+(%d-%d) ='%(y, x, k), y+(x-k))
            g[k][y+(x-k)] = True
    return g

# grid = [[False for x in range(8)] for x in range(8)]
# printgrid(grid)
# for x in range(7, -1, -1):
#     # printgrid(Knightmoves(grid, x, x))
#     printgrid(BishopMoves(grid, x, x))

from Chess import Chess
game = Chess()
print(game.getMoves())
