from Chess import Chess, Player
from Players import *
from MiniMaxPlayer import *

import pygame
from os import sep

# window setup
WINDIM = (1000, 500)
pygame.init()
pygame.display.set_caption('Chess')
DISPLAY = pygame.display.set_mode(WINDIM)
CLOCK = pygame.time.Clock()
FONTSMALL = pygame.font.SysFont(None, 25)
FONTBIG = pygame.font.SysFont(None, 40)

# globals
CENTER = (WINDIM[0]//2, WINDIM[1]//2)
BOARDSIDE = 480
CELLSIDE = BOARDSIDE//8
FPS = 60
BLACK, GREY, WHITE = (0,0,0), (128, 128, 128), (255, 255, 255)
GREYDARK, GREYLIGHT, OFFWHITE = (64, 64, 64), (170, 170, 170), (180, 180, 180)
GREEN , RED_CHECK= (0, 255, 0), (192, 32, 32)
BORDER1, BORDER2, BORDER3 = 1, 2, 3
GAME_RESULT = {
    0: 'ERROR',
    -1: 'Black Wins',
    1: 'White Wins',
    2: 'Game Quit', # TODO: add white/black wins too 2/-2
    3: 'Stalemate',
    4: 'Draw: Insufficient Material',
    5: 'Draw: 3-fold repetition',
    6: 'Draw: 50-move rule',
}

celllogs = False#True#
def log(label, *s, wait=False):
    if label:
        print(*s)
        if wait: input()

# load images
loadPiece = lambda p: pygame.image.load(sep.join(['.', 'assets', 'pieces', p]))
for piece in ['WP', 'BP', 'WK', 'BK', 'WQ', 'BQ', 'WR', 'BR', 'WB', 'BB', 'WN', 'BN']:
    exec("%s = loadPiece('%s.png')"%(piece, piece))
    exec("%s.convert()"%piece)

def blitText(msg, center=CENTER, col=BLACK, bgcol=GREY, font=FONTSMALL, onclick=None, padding=(25, 12), **params):
    text = font.render(msg, True, col)
    cellRect = text.get_rect()
    cellRect.center = center
    bgrect = cellRect.copy()
    bgrect.left -= padding[0]
    bgrect.top -= padding[1]
    bgrect.width += 2*padding[0]
    bgrect.height += 2*padding[1]
    
    mouse = pygame.mouse.get_pos()
    if onclick and bgrect.collidepoint(mouse):
        bgcol = (bgcol[0]+50, bgcol[1]+50, bgcol[2]+50)
        if pygame.mouse.get_pressed()[0]:
            onclick(**params)

    pygame.draw.rect(DISPLAY, bgcol, bgrect)
    DISPLAY.blit(text, cellRect)
    return cellRect

def drawBoard(game:Chess, activeCell=False, center=CENTER, boardSide=BOARDSIDE, options=[], move=[None, None]):
    '''Draws the Board, the pieces, available moves, etc.'''

    blitText('Save Game', onclick=game.save, center=((WINDIM[0]-BOARDSIDE)/4, WINDIM[1]/2))

    for x in range(4, -4, -1):
        for y in range(4, -4, -1): # for each cell to be blited
            
            # display bg
            bcell = (4-x, 4-y)
            bgcol = GREY if (x+y)%2==0 else GREYDARK
            if game.isCheck():
                piece=game.pieceAt((4-x, 4-y))
                if (game.isWhitesMove and piece=='wK') or (not game.isWhitesMove and piece=='bK'):
                    bgcol = RED_CHECK
            pygame.draw.rect(DISPLAY, bgcol, (center[0]-x*CELLSIDE, center[1]-y*CELLSIDE, CELLSIDE, CELLSIDE))

            # display Piece
            # exec('piece=%s'%game.pieceAt(bcell).upper()) # doesn't work
            if game.pieceAt(bcell):
                if game.pieceAt(bcell) == 'wP': piece = WP
                elif game.pieceAt(bcell) == 'bP': piece = BP
                elif game.pieceAt(bcell) == 'wK': piece = WK
                elif game.pieceAt(bcell) == 'bK': piece = BK
                elif game.pieceAt(bcell) == 'wQ': piece = WQ
                elif game.pieceAt(bcell) == 'bQ': piece = BQ
                elif game.pieceAt(bcell) == 'wR': piece = WR
                elif game.pieceAt(bcell) == 'bR': piece = BR
                elif game.pieceAt(bcell) == 'wB': piece = WB
                elif game.pieceAt(bcell) == 'bB': piece = BB
                elif game.pieceAt(bcell) == 'wN': piece = WN
                elif game.pieceAt(bcell) == 'bN': piece = BN
                pr = piece.get_rect()
                pr.center = (center[0]-x*CELLSIDE+CELLSIDE/2, center[1]-y*CELLSIDE+CELLSIDE/2)
                DISPLAY.blit(piece, pr)
                
    pygame.draw.rect(DISPLAY, GREY, 
        (center[0]-boardSide//2-BORDER3, center[1]-boardSide//2-BORDER3, boardSide+BORDER3*2, boardSide+BORDER3*2),
        BORDER3)
    
    color = WHITE if game.isWhitesMove else BLACK
    # mark the active cell
    if activeCell:
        x, y = CENTER[0]-BOARDSIDE/2+CELLSIDE*(activeCell[0]+.05), CENTER[1]-BOARDSIDE/2+CELLSIDE*(activeCell[1]+.05)
        pygame.draw.rect(DISPLAY, color, (x, y, CELLSIDE*.9, CELLSIDE*.9), BORDER1)

    # draw available options of cell
    for option in options:
        op_cell = (4-option[0], 4-option[1])
        x, y = CENTER[0]-op_cell[0]*CELLSIDE+CELLSIDE/2, CENTER[1]-op_cell[1]*CELLSIDE+CELLSIDE/2
        if move[0]:
            pygame.draw.circle(DISPLAY, color, (x, y), CELLSIDE/9)
            if game.isAttackMove(move[0], option):
                pygame.draw.circle(DISPLAY, color, (x, y), CELLSIDE/6, BORDER2)
        else:
            pygame.draw.circle(DISPLAY, color, (x, y), CELLSIDE/9, BORDER2)
            if game.isAttackMove(activeCell, option):
                pygame.draw.circle(DISPLAY, color, (x, y), CELLSIDE/6, BORDER2)

class PlayerUI(Player):

    def chooseMove(self, game:Chess) -> list:
        move = [None, None]
        options = []
        activeCell = [4, 4]

        while True:
            DISPLAY.fill(BLACK)
            events = pygame.event.get()
            for event in events:

                # mouse response
                if event.type == pygame.MOUSEMOTION:
                    x, y = ((event.pos[0]-(CENTER[0]-BOARDSIDE//2))//CELLSIDE, (event.pos[1]-(CENTER[1]-BOARDSIDE//2))//CELLSIDE)
                    if 0<=x<=7 and 0<=y<=7 and activeCell!=[x, y]:
                        activeCell=[x, y]
                        log(celllogs, 'activeCell : %s'%activeCell)
                
                # click handles
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if not move[0]:
                        move[0] = activeCell.copy() if game.pieceAt(activeCell) else None
                    else:
                        move[1] = activeCell.copy()
            
                # keyboard
                elif activeCell and event.type == pygame.KEYDOWN:
                    if event.key==pygame.K_DOWN and activeCell[1]<7: activeCell[1] += 1
                    elif event.key==pygame.K_UP and activeCell[1]>0: activeCell[1] -= 1
                    elif event.key==pygame.K_LEFT and activeCell[0]>0: activeCell[0] -= 1
                    elif event.key==pygame.K_RIGHT and activeCell[0]<7: activeCell[0] += 1
                    elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        if not move[0]:
                            move[0] = activeCell.copy() if game.pieceAt(activeCell) else None
                        else:
                            move[1] = activeCell.copy()
                    log(celllogs, 'activeCell : %s'%activeCell)
                
                elif event.type==pygame.QUIT:
                    pygame.quit()
                    quit()
            
            options=[]
            if not move[0]:
                # no moves made
                selectedPiece = game.pieceAt(activeCell)
                if selectedPiece and ((game.isWhitesMove and selectedPiece[0]=='w') or (not game.isWhitesMove and selectedPiece[0]=='b')):
                    options = game.movesOfCell(activeCell)
            else:
                # selected cell
                selectedPiece = game.pieceAt(move[0])
                if selectedPiece and ((game.isWhitesMove and selectedPiece[0]=='w' ) or (not game.isWhitesMove and selectedPiece[0]=='b')):
                    options = game.movesOfCell(move[0])
                    if not options:
                        # piece can't move: cancel selection
                        move = [None, None]
                else:
                    # selected piece on wrong side
                    options, move = [], [None, None]
                if move[1]:
                    # cell selected for move
                    selectedPiece = game.pieceAt(move[1])
                    if move[0] == move[1]:
                        # clicked same piece: cancel selection
                        options, move = [], [None, None]
                    elif selectedPiece and ((game.isWhitesMove and selectedPiece[0]=='w' ) or (not game.isWhitesMove and selectedPiece[0]=='b')):
                        # clicked another piece on same side
                        options = game.movesOfCell(move[0])
                        move = [move[1], None]
                    elif tuple(move[1]) in options:
                        # valid move made
                        return move
                    else:
                        move = [None , None]
            
            drawBoard(game, activeCell=activeCell, options=options, move=move)
            pygame.display.update()
            CLOCK.tick(FPS)
    
    def choosePromotion(self, game: Chess) -> str:
        # return 'Q' #TODO: under construction
        while True:
            pygame.draw.rect(DISPLAY, BLACK, (CENTER[0]-100, CENTER[1]-100, 200, 200))
            events = pygame.event.get()
            for event in events:
                if event.type==pygame.MOUSEBUTTONDOWN:
                    return 'Q'
            
            pygame.display.update()
            CLOCK.tick(FPS)

def gameOverScreen(game:Chess):
    result = GAME_RESULT[game.result]
    DISPLAY.fill(BLACK)
    drawBoard(game)
    pygame.display.update()
    pygame.time.wait(500)
    while True:
        blitText('Save Game', center=((WINDIM[0]-BOARDSIDE)/4, WINDIM[1]/2), onclick=game.save)
        blitText(result, center=(CENTER[0], CENTER[1]), font=FONTBIG, bgcol=BLACK, col=GREY)
        blitText('press escape to go back', center=(CENTER[0], CENTER[1]*1.3), font=FONTSMALL, bgcol=BLACK, col=GREY)
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.time.wait(500)
                return
        pygame.display.update()
        CLOCK.tick(FPS)


def loadGame():
    bgcol, col = BLACK, GREY
    txt = 'Drop your saved File here'
    while True:
        DISPLAY.fill(BLACK)
        drawBoard(Chess())
        blitText(txt, (CENTER[0], CENTER[1]*0.8), col, bgcol, FONTBIG)
        blitText('press escape to go back', (CENTER[0], CENTER[1]*1.2), col, bgcol)
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.DROPBEGIN:
                bgcol = GREYDARK
            elif event.type in (pygame.DROPFILE, pygame.USEREVENT_DROPFILE):
                file = event.file
                txt = 'loading ' + file.split(sep)[-1]
                blitText(txt, CENTER, col, bgcol, FONTBIG)
                pygame.display.update()
                game = Chess.loadFrom(file)
                main(game)
                return
            elif event.type == pygame.DROPCOMPLETE:
                bgcol = BLACK
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
            elif event.type == pygame.QUIT:
                pygame.quit()
                quit()
        pygame.display.update()
        CLOCK.tick(FPS)

def main(game:Chess=Chess(), white:Player=PlayerUI(), black:Player=PlayerUI()):
    try:
        while not game.result:
            drawBoard(game)
            CLOCK.tick(FPS)
            pygame.display.update()
            pygame.time.wait(500)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

            player = white if game.isWhitesMove else black
            move = player.chooseMove(game)
            if game.pieceAt(move[0])[1] == 'P' and move[1][1] in (0, 7):
                promoteToPiece = player.choosePromotion(game)
            else:
                promoteToPiece = None
            log(celllogs, move)
            game = game.makeMove(*move, promoteTo=promoteToPiece)
        
        gameDescription = '\n'.join([
            GAME_RESULT[game.result],
            f'white: {white.getName()}',
            f'black: {black.getName()}' ])
        game.save(comments=gameDescription)
        gameOverScreen(game)
    except SystemExit:
        raise SystemExit
    except Exception as e:
        # print(e)
        game.save('ERROR_FILE.save.txt')
        gameOverScreen(game)

if __name__=='__main__':

    players = [ PlayerUI(), MinimaxPlayers.latest()(1) ]
    player_white, player_black = players
    
    # Main Menu
    while True:
        DISPLAY.fill(BLACK)
        blitText('Play', (CENTER[0], WINDIM[1]/3), font=FONTBIG, onclick=main, white=player_white, black=player_black)
        blitText('Load Game', (CENTER[0], WINDIM[1]*2/3), font=FONTBIG, onclick=loadGame)

        events = pygame.event.get()
        for event in events:
            if event.type==pygame.QUIT:
                pygame.quit()
                quit()
        pygame.display.update()
        CLOCK.tick(FPS)