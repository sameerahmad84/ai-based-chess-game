"""
This is our driver file and will handle user input and displaying current Game State Object
"""
import math

import pygame as p
from ChessEngine import GameState
from ChessEngine import Move
import SmartMoveFinder
WIDTH = HEIGHT = 512  # width and height of chess board
DIMENSION = 8  # board has 8 rows and 8 columns
#// is floor division operator
SQ_SIZE = WIDTH//DIMENSION  # so that it forms Dimension(8) squares
MAX_FPS = 15
IMAGES = {}

'''
Initialize the global dictionary of pieces image this is an expensive process and would be done only
single time
'''

def loadImages(gs):
    for row_index in range(len(gs.board)):
        if(row_index < 2 or row_index > 5):
            for column in gs.board[row_index]:
                IMAGES[column] = p.transform.scale(p.image.load(f"chess_images/{column}.png"), (SQ_SIZE , SQ_SIZE))
            # we can access an image by saying something such as IMAGES["wp"]

def highlightSquares(screen,gs,validMoves,sqSelected):
    if sqSelected!=():
        r,c=sqSelected
        if gs.board[r][c][0]=="w" if gs.whiteToMove else "b":
            #Highlight Square
            s=p.Surface((SQ_SIZE,SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color("blue"))
            screen.blit(s,(c*SQ_SIZE,r*SQ_SIZE))
            s.fill(p.Color("yellow"))
            for move in validMoves:
                if move.startRow==r and move.startColumn==c:
                    screen.blit(s,(SQ_SIZE*move.endColumn,SQ_SIZE*move.endRow))
''' 
    This is our main driver this will handle user input and updating the graphics
'''

def main():
    #required to initialize all pygame modules
    p.init()
    screen=p.display.set_mode((WIDTH,HEIGHT))
    clock=p.time.Clock()
    screen.fill(p.Color("white"))
    gs = GameState()
    loadImages(gs) # Only Once
    running=True
    sqSelected=()#No square selected initially tuple=>(row,column)
    playerClicks=[]#keeps tracks of square clicks
    validMoves=gs.getValidMoves()
    moveMade=False
    gameOver=False
    player1=True #if a human is playing whilte then it is true,but if ai is playing white it is false
    player2=False #same as above but for black
    while running:
        humanTurn=(gs.whiteToMove and player1) or (not gs.whiteToMove and player2)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type==p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location=p.mouse.get_pos() #get (x,y) of where you want to move the piece
                    column=location[0]//SQ_SIZE
                    row=location[1]//SQ_SIZE
                    if(sqSelected==(row,column)):#clicking on square 2 times to do an undo
                        sqSelected=()
                        playerClicks=[]
                    else:
                        sqSelected=(row,column)
                        playerClicks.append(sqSelected) #append for both 1st and 2nd click
                    if(len(playerClicks)==2):#we have to move a piece
                        m=Move(playerClicks[0],playerClicks[1],gs.board)
                        print(m.getChessNotation())
                        for i in range(len (validMoves)):
                            if m ==validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade=True
                                playerClicks = []
                                sqSelected = ()
                        if not moveMade:
                            playerClicks.pop(0)
            elif e.type==p.KEYDOWN and e.key==p.K_u:
                    gs.undoMove()
                    moveMade=True
        if not gameOver and not humanTurn:
            AIMove=SmartMoveFinder.nega_max_alphaBeta_helper(gs,validMoves)
            #AIMove=SmartMoveFinder.findRandomMoves(validMoves)
            gs.makeMove(AIMove)
            moveMade=True

        if moveMade:
            validMoves=gs.getValidMoves()
            moveMade=False
        drawGameState(screen,gs,validMoves,sqSelected)
        clock.tick(MAX_FPS)
        p.display.flip()

def drawGameState(screen,gs,validMOves,sqSelected):
    drawBoard(screen)
    #add in move suggestions etc
    highlightSquares(screen,gs,validMOves,sqSelected)
    drawPieces(screen,gs.board)


def drawBoard(screen):
    #colors=[p.Color("light grey"),p.Color("dark green")]
    colors = [p.Color(240, 217, 181), p.Color(181, 136, 99)]

    for row in range(DIMENSION):
        for column in range(DIMENSION):
            p.draw.rect(screen,colors[(row+column)%2],p.Rect(column*SQ_SIZE,row*SQ_SIZE,SQ_SIZE,SQ_SIZE))

def drawPieces(screen,board):
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            if(board[row][column]!="--"):
                screen.blit(IMAGES[board[row][column]],(column*SQ_SIZE,row*SQ_SIZE))
if __name__=="__main__":
    main()