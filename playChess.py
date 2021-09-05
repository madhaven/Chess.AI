from Chess import Chess
import pygame

#globals
WINDIM = (600, 600)
CENTER = (WINDIM[0]//2, WINDIM[1]//2)
BOARDSIDE = 480
CELLSIDE = BOARDSIDE//8
FPS = 60
BLACK = (0,0,0)
GREY = (128, 128, 128)
GREEN = (0, 255, 0)
GREYTRANS = (128, 128, 128, 128)
OFFWHITE = (180, 180, 180)
WHITE = (255, 255, 255)
WHITETRANS = (255, 255, 255, 128)
BORDER1, BORDER2, BORDER3 = 1, 2, 3

pygame.init()
pygame.display.set_caption('Chess')
DISPLAY = pygame.display.set_mode(WINDIM)
CLOCK = pygame.time.Clock()
FONTSMALL = pygame.font.SysFont(None, 25)

celllogs=False
def log(label, *s, wait=False):
    if label:
        print(*s)
        if wait: input()

def blitText(msg, center, font, color):
    text = font.render(msg, True, color)
    cellRect = text.get_rect()
    cellRect.center = center
    DISPLAY.blit(text, cellRect)

def drawBoard(game:Chess, center, boardSide:int):
    cellSide = boardSide//8
    for x in range(4, -4, -1):
        for y in range(4, -4, -1): # for each cell to be blited
            
            # display bg
            bcell = (4-x, 4-y)
            if (x+y)%2==0: bgcol, col = GREY, BLACK #white cell
            else: bgcol, col = BLACK, GREY #black cell
            pygame.draw.rect(DISPLAY, bgcol, (center[0]-x*cellSide, center[1]-y*cellSide, cellSide, cellSide))

            # display Piece
            if game.board[bcell[1]][bcell[0]]:
                blitText(game.board[bcell[1]][bcell[0]], (center[0]-x*cellSide+cellSide/2, center[1]-y*cellSide+cellSide/2), FONTSMALL, col)
    pygame.draw.rect(DISPLAY, GREY, 
        (center[0]-boardSide//2-BORDER3, center[1]-boardSide//2-BORDER3, boardSide+BORDER3*2, boardSide+BORDER3*2),
        BORDER3)

def drawSelectedCell(cell):
    x, y = CENTER[0]-BOARDSIDE/2+CELLSIDE*(cell[0]+.05), CENTER[1]-BOARDSIDE/2+CELLSIDE*(cell[1]+.05)
    pygame.draw.rect(DISPLAY, OFFWHITE, (x, y, CELLSIDE*.9, CELLSIDE*.9), BORDER1)

def drawOptions(game, cell):
    # print options if mouse over valid cell
    x, y = cell[0], cell[1]
    if not game.board[y][x]: return
    elif ( game.isWhitesMove and game.board[y][x][0]=='w' or not game.isWhitesMove and game.board[y][x][0]=='b'):
        moves = game.movesOf((x,y))
    else:
        moves = game.legalMoves((x, y))
    for option in moves:
        op_cell = (4-option[0], 4-option[1])
        pygame.draw.circle(DISPLAY, OFFWHITE, (CENTER[0]-op_cell[0]*CELLSIDE+CELLSIDE/2, CENTER[1]-op_cell[1]*CELLSIDE+CELLSIDE/2), CELLSIDE/9)
    return moves

def main():
    game = Chess()
    boardState='waitingForSelection'
    cell = [7, 7]
    move = [None, None]
    while True:
        events = pygame.event.get()
        for event in events:
            # print(event)
            if event.type==pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type==pygame.MOUSEMOTION:
                x, y=((event.pos[0]-(CENTER[0]-BOARDSIDE//2))//CELLSIDE, (event.pos[1]-(CENTER[1]-BOARDSIDE//2))//CELLSIDE)
                if 0<=x<=7 and 0<=y<=7 and cell!=[x, y]:
                    cell=[x, y]
                    log(celllogs, cell)
            elif event.type==pygame.MOUSEBUTTONUP:
                x, y=((event.pos[0]-(CENTER[0]-BOARDSIDE//2))//CELLSIDE, (event.pos[1]-(CENTER[1]-BOARDSIDE//2))//CELLSIDE)
                if not move[0]: move[0] = [x, y] if 0<=x<=7 and 0<=y<=7 else None
                else: move[1] = [x, y] if 0<=x<=7 and 0<=y<=7 else None
            elif cell and event.type==pygame.KEYUP: # keyboard
                if event.key==pygame.K_DOWN and cell[1]<7: cell[1] += 1
                elif event.key==pygame.K_UP and cell[1]>0: cell[1] -= 1
                elif event.key==pygame.K_LEFT and cell[0]>0: cell[0] -= 1
                elif event.key==pygame.K_RIGHT and cell[0]<7: cell[0] += 1
                elif event.key==pygame.K_SPACE:
                    if not move[0]: move[0] = cell
                    else: move[1] = cell
                log(celllogs, cell)
                    
        drawBoard(game, (WINDIM[0]//2, WINDIM[1]//2), BOARDSIDE)
        drawSelectedCell(cell)
        if boardState == 'waitingForSelection':
            if cell: drawOptions(game, cell)
            if move[0]:
                boardState = 'waitingForMove'
                log(celllogs, boardState, cell, move)
        elif boardState == 'waitingForMove':
            validMoves = drawOptions(game, move[0])
            if move[1]:
                if move[1]!=move[0] and tuple(move[1]) in validMoves:
                    game = game.makeMove(move[0], move[1])
                move=[None, None]
                boardState = 'waitingForSelection'
                log(celllogs, boardState, cell, move)
        
        pygame.display.update()
        CLOCK.tick(FPS)

if __name__=='__main__': main()