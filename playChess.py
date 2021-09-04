from pygame import transform
from Chess import Chess
import pygame

#globals
WINDIM = (600, 600)
FPS = 60
BLACK = (0,0,0)
GREY = (128, 128, 128)
GREEN = (0, 255, 0)
GREYTRANS = (128, 128, 128, 128)
WHITE = (255, 255, 255)
WHITETRANS = (255, 255, 255, 128)
BORDER1, BORDER2, BORDER3 = 1, 2, 3
BOARDSIZE = 480

pygame.init()
pygame.display.set_caption('Chess')
DISPLAY = pygame.display.set_mode(WINDIM)
CLOCK = pygame.time.Clock()
FONTSMALL = pygame.font.SysFont(None, 25)

def drawBoard(game:Chess, center, sideLength:int):
    radius = sideLength//2
    cellSide = sideLength//8
    mouse = pygame.mouse.get_pos()
    mouseCell = False
    # mouse = (mouse[0]-center[0], mouse[1]-center[1])
    pygame.draw.rect(DISPLAY, GREY, (center[0]-radius, center[1]-radius, sideLength, sideLength), BORDER3)
    for x in range(4, -4, -1):
        for y in range(4, -4, -1): # for each cell to be blited
            
            # display bg
            cell = (4-x, 4-y)
            if (x+y)%2==0: bgcol, col = GREY, BLACK #white cell
            else: bgcol, col = BLACK, GREY #black cell
            pygame.draw.rect(DISPLAY, bgcol, (center[0]-x*cellSide, center[1]-y*cellSide, cellSide, cellSide))

            # hover response
            if (0 < mouse[0]-(center[0]-x*cellSide) < cellSide
                and 0 < mouse[1]-(center[1]-y*cellSide) < cellSide
                and game.board[cell[1]][cell[0]] and (
                    game.isWhitesMove and game.board[cell[1]][cell[0]][0]=='w'
                    or not game.isWhitesMove and game.board[cell[1]][cell[0]][0]=='b'
                )):
                mouseCell = cell
                pygame.draw.circle(DISPLAY, WHITE, (center[0]-x*cellSide+cellSide/2, center[1]-y*cellSide+cellSide/2), cellSide/2, BORDER2)

            # display Piece
            if game.board[cell[1]][cell[0]]:                    
                cellText = FONTSMALL.render(game.board[cell[1]][cell[0]], True, col)
                cellRect = cellText.get_rect()
                cellRect.center = (center[0]-x*cellSide+cellSide/2, center[1]-y*cellSide+cellSide/2)
                DISPLAY.blit(cellText, cellRect)

    # print options if mouse over valid cell
    if mouseCell:
        for option in game.legalMoves(mouseCell):
            op_cell = (4-option[0], 4-option[1])
            # opcolbg, opcol = (GREY, BLACK) if (op_cell[0]+op_cell[1])%2==0 else (BLACK, GREY)
            pygame.draw.circle(DISPLAY, WHITE, (center[0]-op_cell[0]*cellSide+cellSide/2, center[1]-op_cell[1]*cellSide+cellSide/2), cellSide/8)

def main():
    chess = Chess()
    while True:
        for event in pygame.event.get():
            # print(event)
            if event.type==pygame.QUIT:
                pygame.quit()
                quit()
        drawBoard(chess, (WINDIM[0]//2, WINDIM[1]//2), BOARDSIZE)

        pygame.display.update()
        CLOCK.tick(FPS)

if __name__=='__main__': main()