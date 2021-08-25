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

def moves(grid, x, y):
    g=deepcopy(grid)
    for dy in range(y-2, y+3):
        for dx in range(x-2, x+3):
            print('cell', dx, dy,':', end='')
            if 0<=dx<8 and 0<=dy<8 and dx!=x and dy!=y and abs(dx-x)!=abs(dy-y):
                g[dy][dx]=True
    return g

grid = [[False for x in range(8)] for x in range(8)]
printgrid(grid)
for x in range(7, -1, -1):
    printgrid(moves(grid, x, x))
