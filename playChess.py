from Chess import Chess
import pygame
from os import sep

WINDIM = (1000, 500)
pygame.init()
pygame.display.set_caption('Chess')
DISPLAY = pygame.display.set_mode(WINDIM)
CLOCK = pygame.time.Clock()
FONTSMALL = pygame.font.SysFont(None, 25)

#globals
CENTER = (WINDIM[0]//2, WINDIM[1]//2)
BOARDSIDE = 480
CELLSIDE = BOARDSIDE//8
FPS = 60
BLACK = (0,0,0)
# GREYDARK = (84, 84, 84)
GREYDARK = (64, 64, 64)
GREY = (128, 128, 128)
GREYLIGHT = (170, 170, 170)
GREEN = (0, 255, 0)
GREYTRANS = (128, 128, 128, 128)
OFFWHITE = (180, 180, 180)
WHITE = (255, 255, 255)
WHITETRANS = (255, 255, 255, 128)
BORDER1, BORDER2, BORDER3 = 1, 2, 3

loadPiece = lambda p: pygame.image.load(sep.join(['.','assets','pieces',p]))
for piece in ['WP', 'BP', 'WK', 'BK', 'WQ', 'BQ', 'WR', 'BR', 'WB', 'BB', 'WN', 'BN']:
    exec("%s = loadPiece('%s.png')"%(piece, piece))
    exec("%s.convert()"%piece)

celllogs=False
def log(label, *s, wait=False):
    if label:
        print(*s)
        if wait: input()

def blitText(msg, center, color, font=FONTSMALL):
    text = font.render(msg, True, color)
    cellRect = text.get_rect()
    cellRect.center = center
    DISPLAY.blit(text, cellRect)

def saveGameButton(game, x, y, bgcol, col):
    l, w = 60, 25
    mouse = pygame.mouse.get_pos()
    if x-l < mouse[0] < x+l and y-w < mouse[1] < y+w:
        bgcol = (bgcol[0]+50, bgcol[1]+50, bgcol[2]+50)
        if pygame.mouse.get_pressed()[0]:
            game.save()
    pygame.draw.rect(DISPLAY, bgcol, (x-l, y-w, 2*l, 2*w))
    blitText('Save Game', (x,y), col)


def drawBoard(game:Chess, center, boardSide:int):
    '''Draws the Board, the pieces'''
    cellSide = boardSide//8
    for x in range(4, -4, -1):
        for y in range(4, -4, -1): # for each cell to be blited
            
            # display bg
            bcell = (4-x, 4-y)
            if (x+y)%2==0: bgcol, col = GREY, BLACK #white cell
            else: bgcol, col = GREYDARK, GREY #black cell
            pygame.draw.rect(DISPLAY, bgcol, (center[0]-x*cellSide, center[1]-y*cellSide, cellSide, cellSide))

            # display Piece
            if game.board[bcell[1]][bcell[0]]:
                if game.board[bcell[1]][bcell[0]]=='wP': piece = WP
                elif game.board[bcell[1]][bcell[0]]=='bP': piece = BP
                elif game.board[bcell[1]][bcell[0]]=='wK': piece = WK
                elif game.board[bcell[1]][bcell[0]]=='bK': piece = BK
                elif game.board[bcell[1]][bcell[0]]=='wQ': piece = WQ
                elif game.board[bcell[1]][bcell[0]]=='bQ': piece = BQ
                elif game.board[bcell[1]][bcell[0]]=='wR': piece = WR
                elif game.board[bcell[1]][bcell[0]]=='bR': piece = BR
                elif game.board[bcell[1]][bcell[0]]=='wB': piece = WB
                elif game.board[bcell[1]][bcell[0]]=='bB': piece = BB
                elif game.board[bcell[1]][bcell[0]]=='wN': piece = WN
                elif game.board[bcell[1]][bcell[0]]=='bN': piece = BN
                pr = piece.get_rect()
                pr.center = (center[0]-x*cellSide+cellSide/2, center[1]-y*cellSide+cellSide/2)
                DISPLAY.blit(piece, pr)
                
    pygame.draw.rect(DISPLAY, GREY, 
        (center[0]-boardSide//2-BORDER3, center[1]-boardSide//2-BORDER3, boardSide+BORDER3*2, boardSide+BORDER3*2),
        BORDER3)

def markActiveCell(cell):
    '''Draws a border on the active cell'''
    x, y = CENTER[0]-BOARDSIDE/2+CELLSIDE*(cell[0]+.05), CENTER[1]-BOARDSIDE/2+CELLSIDE*(cell[1]+.05)
    pygame.draw.rect(DISPLAY, OFFWHITE, (x, y, CELLSIDE*.9, CELLSIDE*.9), BORDER1)

def drawOptions(game, cell):
    '''draw available options of cell'''
    x, y = cell[0], cell[1]
    if not game.board[y][x]: return
    elif ((game.isWhitesMove and game.board[y][x][0]=='w') or (not game.isWhitesMove and game.board[y][x][0]=='b')):
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
    activeCell = [7, 7]
    move = [None, None]
    while True:
        events = pygame.event.get()
        for event in events:
            # event handling
            # print(event)
            if event.type==pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type==pygame.MOUSEMOTION:
                x, y=((event.pos[0]-(CENTER[0]-BOARDSIDE//2))//CELLSIDE, (event.pos[1]-(CENTER[1]-BOARDSIDE//2))//CELLSIDE)
                if 0<=x<=7 and 0<=y<=7 and activeCell!=[x, y]:
                    activeCell=[x, y]
                    log(celllogs, 'activeCell : %s'%activeCell)
            elif event.type==pygame.MOUSEBUTTONUP:
                x, y=((event.pos[0]-(CENTER[0]-BOARDSIDE//2))//CELLSIDE, (event.pos[1]-(CENTER[1]-BOARDSIDE//2))//CELLSIDE)
                if not move[0]: move[0] = [x, y] if 0<=x<=7 and 0<=y<=7 and game.board[activeCell[1]][activeCell[0]] else None
                else: move[1] = [x, y] if 0<=x<=7 and 0<=y<=7 else None
            elif activeCell and event.type==pygame.KEYUP: # keyboard
                if event.key==pygame.K_DOWN and activeCell[1]<7: activeCell[1] += 1
                elif event.key==pygame.K_UP and activeCell[1]>0: activeCell[1] -= 1
                elif event.key==pygame.K_LEFT and activeCell[0]>0: activeCell[0] -= 1
                elif event.key==pygame.K_RIGHT and activeCell[0]<7: activeCell[0] += 1
                elif event.key==pygame.K_SPACE:
                    if not move[0]: 
                        if game.board[activeCell[1]][activeCell[0]]: move[0] = activeCell
                    else: move[1] = activeCell
                log(celllogs, 'activeCell : %s'%activeCell)
        
        # Game Logic to events
        drawBoard(game, (WINDIM[0]//2, WINDIM[1]//2), BOARDSIDE)
        saveGameButton(game, (WINDIM[0]-BOARDSIDE)/4, (WINDIM[0]-BOARDSIDE)/4, GREY, BLACK)
        markActiveCell(activeCell)
        if boardState == 'waitingForSelection':
            if activeCell: 
                validMoves = drawOptions(game, activeCell)
            if move[0]:
                boardState = 'waitingForMove'
                log(celllogs, boardState, activeCell, move)
        elif boardState == 'waitingForMove':
            validMoves = drawOptions(game, move[0])
            if move[1]:
                if move[1]!=move[0] and tuple(move[1]) in validMoves:
                    game = game.makeMove(move[0], move[1])
                move=[None, None]
                boardState = 'waitingForSelection'
                log(celllogs, boardState, activeCell, move)
        pygame.display.update()
        CLOCK.tick(FPS)

if __name__=='__main__': main()