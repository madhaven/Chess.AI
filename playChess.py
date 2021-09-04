from pygame import transform
from Chess import Chess
import pygame

#globals
WINDIM = (600, 600)
FPS = 60
BLACK = (0,0,0)
GREY = (128, 128, 128)
GREYTRANS = (128, 128, 128, 128)
WHITE = (255, 255, 255)
WHITETRANS = (255, 255, 255, 128)
BORDER1, BORDER2, BORDER3 = 1, 2, 3

pygame.init()
pygame.display.set_caption('Chess')
display = pygame.display.set_mode(WINDIM)
clock = pygame.time.Clock()

def drawBoard(game:Chess, center, sideLength:int):
    radius = sideLength//2
    cellSide = sideLength//8
    mouse = pygame.mouse.get_pos()
    # mouse = (mouse[0]-center[0], mouse[1]-center[1])
    pygame.draw.rect(display, GREY, (center[0]-radius, center[1]-radius, sideLength, sideLength), BORDER3)
    for x in range(4, -4, -1):
        for y in range(4, -4, -1):
            if 0 < mouse[0]-(center[0]-x*cellSide) < cellSide and 0 < mouse[1]-(center[1]-y*cellSide) < cellSide: highlight = True
            else: highlight = False
                
            if (x+y)%2==0:
                pygame.draw.rect(display, GREY, (center[0]-x*cellSide, center[1]-y*cellSide, cellSide, cellSide))
                if highlight:
                    pygame.draw.circle(display, BLACK, (center[0]-x*cellSide+cellSide/2, center[0]-y*cellSide+cellSide/2), cellSide/2, BORDER2)
            else:
                if highlight:
                    pygame.draw.circle(display, GREY, (center[0]-x*cellSide+cellSide/2, center[0]-y*cellSide+cellSide/2), cellSide/2, BORDER2)

def main():
    chess = Chess()

    while True:
        display.fill(BLACK)
        for event in pygame.event.get():
            # print(event)
            if event.type==pygame.QUIT:
                pygame.quit()
                break
        drawBoard(chess, (WINDIM[0]//2, WINDIM[1]//2), 480)

        pygame.display.update()
        clock.tick(FPS)

if __name__=='__main__': main()