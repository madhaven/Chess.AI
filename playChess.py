from Chess import Chess, Player
from Players import *
from MiniMaxPlayer import *

import traceback
import threading
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
    0: 'ERROR', # TODO: error / in progress?
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
    exec(f"{piece} = loadPiece('{piece}.png')")
    exec(f"{piece}.convert()")

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

    DISPLAY.fill(BLACK)
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
            if not game.pieceAt(bcell): continue
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

def drawPromotionMenu(game:Chess, activeOption:int=None, center=CENTER, boardSide=BOARDSIDE, pieceOrder:str='RQBN'):
    promoStart = center[0] - boardSide // 2
    bgColor = BLACK if game.isWhitesMove else WHITE
    fgColor = WHITE if game.isWhitesMove else BLACK
    pieceMap = {'R':[BR, WR], 'Q':[BQ, WQ], 'B':[BB, WB], 'N':[BN, WN] }
    pieceWidth = boardSide // 4

    DISPLAY.fill(bgColor)
    pygame.draw.rect(DISPLAY, bgColor, (promoStart, center[1]-boardSide//2, boardSide, boardSide))
    for i, piece in enumerate(pieceOrder):
        icon = pieceMap[piece][game.isWhitesMove]
        rect = icon.get_rect()
        rect.center = (promoStart + ((i+.5) * pieceWidth), center[1])
        DISPLAY.blit(icon, rect)

    if activeOption != None:
        rectParams = (promoStart + (activeOption * pieceWidth), center[1]-boardSide//8, pieceWidth, pieceWidth)
        pygame.draw.rect(DISPLAY, fgColor, rectParams, BORDER1)

class PlayerUI(Player):

    def chooseMove(self, game:Chess) -> list:
        move = [None, None]
        options = []
        activeCell = [4, 4]

        while True:
            events = pygame.event.get()
            for event in events:

                # mouse response
                if event.type == pygame.MOUSEMOTION:
                    x, y = ((event.pos[0]-(CENTER[0]-BOARDSIDE//2))//CELLSIDE, (event.pos[1]-(CENTER[1]-BOARDSIDE//2))//CELLSIDE)
                    if 0<=x<=7 and 0<=y<=7 and activeCell!=[x, y]:
                        activeCell = [x, y]
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
                    safe_quit()
            
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
        activeOption = None
        pieceOrder = 'NQBR'

        while True:
            drawPromotionMenu(game=game, activeOption=activeOption, pieceOrder=pieceOrder)
            pygame.display.update()
            CLOCK.tick(FPS)

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.MOUSEMOTION:
                    x = (event.pos[0]-(CENTER[0]-BOARDSIDE//2))//(CELLSIDE*2)
                    if activeOption != x and 0 <= x < 4:
                        activeOption = x
                elif event.type == pygame.MOUSEBUTTONDOWN: return pieceOrder[activeOption]
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        if activeOption == None: activeOption = 0
                        else: activeOption = (activeOption + 1) % 4
                    elif event.key == pygame.K_LEFT:
                        if activeOption == None: activeOption = 3
                        else: activeOption = (activeOption - 1) % 4
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        return pieceOrder[activeOption]
                elif event.type == pygame.QUIT: safe_quit()

def gameOverScreen(game:Chess):
    result = GAME_RESULT[game.result]
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
                safe_quit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.time.wait(500)
                return
        pygame.display.update()
        CLOCK.tick(FPS)

def loadGame():
    bgcol, col = BLACK, GREY
    txt = 'Drop your saved File here'
    while True:
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
                safe_quit()
        pygame.display.update()
        CLOCK.tick(FPS)
    
def thread_choose_move(player: Player, game: Chess, info: dict):
    info['move'] = player.chooseMove(game)
    info['running'] = False
    info['thread'] = False

def thread_choose_promotion(player: Player, game: Chess, info: dict):
    info['promotion'] = player.choosePromotion(game)
    info['running'] = False
    info['thread'] = False

def start_thread(target, thread_info, *args, **kwargs):
    try:
        kwargs['info'] = thread_info
        thread = threading.Thread(target=target, daemon=True, args=args, kwargs=kwargs)
        thread_info['running'] = True
        thread_info['thread'] = thread
        thread.start()
    except Exception as ex:
        print(f"Error in threaded task: {ex}")
        print(traceback.format_exc())

def safe_quit():
    threads = threading.enumerate()
    main_thread = threading.main_thread()
    for thread in threads:
        if thread == main_thread:
            continue
        print('terminating', thread.name)
        thread.join(0)
    pygame.quit()
    quit()

def main(game: Chess = Chess(), white: Player = PlayerUI(), black: Player = PlayerUI()):
    thread_info = { "move": None, "promotion": False, "running": False, "thread": False }
    try:
        while not game.result:
            drawBoard(game)
            player = white if game.isWhitesMove else black
            CLOCK.tick(FPS)
            pygame.display.update()

            # handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    safe_quit()
            
            # skip other checks if thread is running
            if thread_info['running']:
                continue

            if thread_info['move'] is not None:
                move = thread_info['move']
            elif isinstance(player, PlayerUI):
                thread_info['move'] = player.chooseMove(game)
                continue
            else:
                start_thread(thread_choose_move, thread_info, player, game)
                pygame.time.wait(500)
                continue

            # TODO: REFINE PROMOTION MECHANISM
            if game.pieceAt(move[0])[1] != 'P' or move[1][1]%7 != 0:
                promotion = None
            elif thread_info['promotion'] is not False:
                promotion = thread_info['promotion']
            elif isinstance(player, PlayerUI):
                thread_info['promotion'] = player.choosePromotion(game)
                continue
            else:
                start_thread(thread_choose_promotion, thread_info, player, game)
                pygame.time.wait(500)
                continue
            
            game = game.makeMove(*move, promoteTo=promotion)
            thread_info['move'] = None
            thread_info['promotion'] = False
            log(celllogs, move)
        
        # GAME OVER
        gameDescription = '\n'.join([
            GAME_RESULT[game.result],
            f'white: {white.getName()}',
            f'black: {black.getName()}'
        ])
        game.save(comments=gameDescription)
        gameOverScreen(game)
    
    except Exception as e:
        print(f'error: {str(e)}')
        print(traceback.format_exc())
        game.save('ERROR_FILE.save.txt')
        gameOverScreen(game)

def gameMenu(white: Player, black: Player):
    while True:
        DISPLAY.fill(BLACK)
        blitText('Play', (CENTER[0], WINDIM[1]/3), font=FONTBIG, onclick=main, white=white, black=black)
        blitText('Load Game', (CENTER[0], WINDIM[1]*2/3), font=FONTBIG, onclick=loadGame)

        events = pygame.event.get()
        for event in events:
            if event.type==pygame.QUIT:
                safe_quit()
        
        pygame.display.update()
        CLOCK.tick(FPS)

if __name__ == '__main__':
    white, black = [
        # PlayerUI(),
        # MinimaxPlayer_04_t(3, 20),
        MinimaxPlayer_04_01(3),
        MinimaxPlayer_04_01(2),
        # PlayerUI(),
    ]
    # main(Chess.loadFrom('./assets/sampleGames/chess_promotionTest.save.txt'))
    gameMenu(white, black)