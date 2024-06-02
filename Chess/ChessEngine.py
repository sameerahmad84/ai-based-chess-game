"""
This class is responsible for storing all the information for current state of game. It is also going to
be responsible for determining the valid modes.It will also keep a mode log
"""
class GameState:
    def __init__(self):
        # 8x8 2D list each piece is represented by 2 characters...
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.whiteToMove=True
        self.moveLog=[]
        self.moveFunctions={
            'p':self.getPawnMoves,'R':self.getRookMoves,'N':self.getNightMoves,'B':self.getBishopMoves,
            'Q':self.getQueenMoves,'K':self.getKingMoves
        }
        self.whiteKingLocation=(7,4)
        self.blackKingLocation=(0,4)
        self.checkmate=False
        self.stalemate=False
        self.enpassantPossible=()
        self.currentCastlingRights=CastleRights(True,True,True,True)
        self.castlingRightsLog=[CastleRights(self.currentCastlingRights.wks,self.currentCastlingRights.bks,self.currentCastlingRights.wqs,self.currentCastlingRights.bqs)]

    #This function takes a move object and makes a move will not work for castling,en-psaunt,pawn promotion
    def makeMove(self,move):
        self.board[move.startRow][move.startColumn]="--"
        self.board[move.endRow][move.endColumn]=move.pieceMoved
        self.moveLog.append(move)#save history or to undo move
        self.whiteToMove=not self.whiteToMove
        if(move.pieceMoved=="bK"):
            self.blackKingLocation=(move.endRow,move.endColumn)
        elif move.pieceMoved=="wK":
            self.whiteKingLocation=(move.endRow, move.endColumn)
        if move.isPawnPromotion:
            self.board[move.endRow][move.endColumn] = move.pieceMoved[0]+"Q"
        if move.isEnpassantMove:
            self.board[move.startRow][move.endColumn]="--"
        if move.isCastleMove:
            if move.endColumn-move.startColumn==2:#king side castle move
                self.board[move.endRow][move.endColumn-1]=self.board[move.endRow][move.endColumn+1]
                self.board[move.endRow][move.endColumn + 1]="--"
            else:
                self.board[move.endRow][move.endColumn + 1] = self.board[move.endRow][move.endColumn - 2]
                self.board[move.endRow][move.endColumn -2] = "--"

        if move.pieceMoved[1]=="p" and abs(move.endRow-move.startRow)==2:
            #enpassant exixts on two jump move
            self.enpassantPossible=((move.startRow+move.endRow)//2,move.endColumn)
        else:
            self.enpassantPossible=()
        self.updateCastleRight(move)
        self.castlingRightsLog.append(CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                                   self.currentCastlingRights.wqs,self.currentCastlingRights.bqs))

    #update castle rights if it is a king or rook move
    def updateCastleRight(self,move):
        if move.pieceMoved=="wK":
            self.currentCastlingRights.wks=False
            self.currentCastlingRights.wqs=False
        if move.pieceMoved=="bK":
            self.currentCastlingRights.bks=False
            self.currentCastlingRights.bqs=False
        if move.pieceMoved=="wR":
            if move.startRow==7:
                if move.startColumn==7:
                    self.currentCastlingRights.wks=False
                if move.startColumn==0:
                    self.currentCastlingRights.wqs=False
        elif move.pieceMoved=="bR":
            if move.startRow==0:
                if move.startColumn==7:
                    self.currentCastlingRights.bks=False
                if move.startColumn==0:
                    self.currentCastlingRights.bqs=False


    def undoMove(self):
        if len(self.moveLog)!=0:
            move=self.moveLog.pop()
            self.board[move.startRow][move.startColumn]=move.pieceMoved
            self.board[move.endRow][move.endColumn]=move.pieceCaptured
            self.whiteToMove=not self.whiteToMove
            if (move.pieceMoved == "bK"):
                self.blackKingLocation=(move.startRow, move.startColumn)
            elif move.pieceMoved == "wK":
                self.whiteKingLocation=(move.startRow, move.startColumn)
            if move.isEnpassantMove:
                self.board[move.endRow][move.endColumn] = "--" #clear the landing sqyare
                self.board[move.startRow][move.endColumn]=move.pieceCaptured
                self.enpassantPossible=(move.endRow,move.endColumn)

            #undo a two piece pawn move
            if move.pieceMoved[1]=="p" and abs (move.startRow-move.endRow)==2:
                self.enpassantPossible=()
            #undo castling rights
            self.castlingRightsLog.pop()#get rid of last castle right which we undo
            # self.currentCastlingRights=self.castlingRightsLog[-1]#setting current castle right again
            self.currentCastlingRights.wks=self.castlingRightsLog[-1].wks
            self.currentCastlingRights.bks=self.castlingRightsLog[-1].bks
            self.currentCastlingRights.wqs = self.castlingRightsLog[-1].wqs
            self.currentCastlingRights.bqs = self.castlingRightsLog[-1].bqs
            #undo castle move
            if move.isCastleMove:
                if move.endColumn-move.startColumn==2:#king side
                    self.board[move.startRow][move.endColumn+1]=self.board[move.startRow][move.endColumn-1]
                    self.board[move.endRow][move.endColumn-1]="--"
                else:#queen side
                    self.board[move.endRow][move.endColumn-2]=self.board[move.endRow][move.endColumn+1]
                    self.board[move.endRow][move.endColumn + 1]="--"


    #get all possible moves considering checks
    def getValidMoves(self):
        tempEnpassantPossible=self.enpassantPossible
        tempCurrentCastlingRights=CastleRights(self.currentCastlingRights.wks,self.currentCastlingRights.bks,self.currentCastlingRights.wqs,self.currentCastlingRights.bqs)
        #1.)for a given turn generate all moves
        moves=self.getPossibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0],self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0],self.blackKingLocation[1], moves)
        #2.)Now for each move make a move
        for i in range(len(moves)-1,-1,-1):#iterate the list backwards if you want to remove from it
            self.makeMove(moves[i])
            self.whiteToMove=not  self.whiteToMove
            # 3.)For each move generate opponent moves
            # 4.)Check if they attack your king if they mark that move in step 2 as invalid
            if(self.inCheck()):
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()

        if(len(moves)==0):
            if(self.inCheck()):
                self.checkmate=True
            else:
               self.stalemate=True
        else:
            self.checkmate=False
            self.stalemate=False
        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRights=tempCurrentCastlingRights
        return moves



    #Determine if the current player is in chk
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0],self.whiteKingLocation[1])
        elif not self.whiteToMove:
            return self.squareUnderAttack(self.blackKingLocation[0],self.blackKingLocation[1])
    #determine if the enemie can attck the square r,c
    def squareUnderAttack(self,r,c):
        self.whiteToMove=not self.whiteToMove
        oppMoves=self.getPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow==r and move.endColumn==c:
                return True
        return False
    #get all possible moves without considerin checks
    def getPossibleMoves(self):
        moves=[]
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn=self.board[r][c][0]
                piece=self.board[r][c][1]
                if (self.whiteToMove and turn=='w') or (not self.whiteToMove and turn=='b'):
                    self.moveFunctions[piece](r,c,moves)
        return moves




    #Get all the moves of a pawn on specific row and column and append it to the list
    def getPawnMoves(self,r,c,moves):
        if self.whiteToMove:
            if r-1 >=0 and self.board[r-1][c]=="--":
                moves.append(Move((r,c),(r-1,c),self.board))
                if r-2 >=0 and self.board[r-2][c]=="--" and r==6:
                    moves.append(Move((r,c),(r-2,c),self.board))
            if c-1>=0:
                if self.board[r-1][c-1][0]=="b":
                    moves.append(Move((r,c),(r-1,c-1),self.board))
                elif (r-1,c-1)==self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board,isEnpassantMove=True))
            if c+1<=7:
                if self.board[r-1][c+1][0]=="b":
                    moves.append(Move((r,c),(r-1,c+1),self.board))
                elif (r-1,c+1)==self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board,isEnpassantMove=True))

        else:
            if r+1<=7 and self.board[r+1][c]=="--":
                moves.append(Move((r,c),(r+1,c),self.board))
                if r+2<=7 and self.board[r+2][c]=="--" and r==1:
                    moves.append(Move((r,c),(r+2,c),self.board))
            if c-1>=0:
                if self.board[r+1][c-1][0]=="w":
                    moves.append(Move((r,c),(r+1,c-1),self.board))
                elif self.board[r+1][c-1]==self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board),isEnpassantMove=True)
            if c+1<=7:
                if self.board[r+1][c+1][0]=="w":
                    moves.append(Move((r,c),(r+1,c+1),self.board))
                elif self.board[r+1][c+1]==self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board),isEnpassantMove=True)




    # Get all the moves of a rook on specific row and column and append it to the list
    def getRookMoves(self,r,c,moves):
        enemyColor="b" if self.whiteToMove else "w"
        direction=[(-1,0),(1,0),(0,-1),(0,1)]#bottom,top,left,right
        for d in direction:
            for i in range(1,8):
                endRow=r+d[0]*i
                endColumn=c+d[1]*i
                if 0<=endRow<=7 and 0<=endColumn<=7:
                    if(self.board[endRow][endColumn]=="--"):
                        moves.append(Move((r,c),(endRow,endColumn),self.board))
                    else:
                        if self.board[endRow][endColumn][0]==enemyColor:
                            moves.append(Move((r, c), (endRow, endColumn), self.board))
                        break
                else:
                    break

    def getBishopMoves(self,r,c,moves):
        enemyColor = "b" if self.whiteToMove else "w"
        direction = [(-1, -1), (1, 1), (1, -1), (-1, 1)]  #top-left,bottom-right,bottom-left,top-right
        for d in direction:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endColumn = c + d[1] * i
                if 0 <= endRow <= 7 and 0 <= endColumn <= 7:
                    if (self.board[endRow][endColumn] == "--"):
                        moves.append(Move((r, c), (endRow, endColumn), self.board))
                    else:
                        if self.board[endRow][endColumn][0] == enemyColor:
                            moves.append(Move((r, c), (endRow, endColumn), self.board))
                        break
                else:
                    break


    def getNightMoves(self,r,c,moves):
        allyColor="w" if self.whiteToMove else "b"
        knightMoves=[(2,-1),(-2,-1),(-1,2),(-1,-2),(-2,1),(2,1),(-1,-2),(1,-2)]
        for move in knightMoves:
            endRow=r+move[0]
            endColumn=c+move[1]
            if 0 <= endRow <= 7 and 0 <= endColumn <= 7:
                if(self.board[endRow][endColumn][0]!=allyColor):
                    moves.append(Move((r, c), (endRow, endColumn), self.board))


    def getQueenMoves(self,r,c,moves):
        self.getRookMoves(r,c,moves)
        self.getBishopMoves(r,c,moves)


    def getKingMoves(self,r,c,moves):
        allyColor="w" if self.whiteToMove else "b"
        kingMoves=[(0,1),(0,-1),(1,1),(-1,-1),(1,0),(-1,0),(1,-1),(-1,1)]
        for i in range(8):
            rowEnd=r+kingMoves[i][0]
            columnEnd=c+kingMoves[i][1]
            if 0<=rowEnd<=7 and 0<=columnEnd<=7:
                if self.board[rowEnd][columnEnd][0]!=allyColor:
                    moves.append(Move((r,c),(rowEnd,columnEnd),self.board))

    def getCastleMoves(self,r,c,moves):
        if self.inCheck():
            return
        if (self.whiteToMove and self.currentCastlingRights.wks) or ((not self.whiteToMove) and self.currentCastlingRights.bks):
            self.getKingSideCastleMoves(r,c,moves)
        if (self.whiteToMove and self.currentCastlingRights.wqs) or ((not self.whiteToMove) and self.currentCastlingRights.bqs):
            self.getQueenSideCastleMoves(r,c,moves)

    def getKingSideCastleMoves(self,r,c,moves):
        if self.board[r][c+1]=="--" and self.board[r][c+2]=="--":
            if (not self.squareUnderAttack(r,c+1)) and (not self.squareUnderAttack(r,c+2)):
                moves.append(Move((r,c),(r,c+2),self.board,isCastleMove=True))

    def getQueenSideCastleMoves(self, r, c, moves):
        if self.board[r][c-1]=="--" and self.board[r][c-2]=="--" and self.board[r][c-3]=="--":
            if not self.squareUnderAttack(r,c-1) and not self.squareUnderAttack(r,c-2):
                moves.append(Move((r,c),(r,c-2),self.board,isCastleMove=True))


class CastleRights:
    def __init__(self,wks,bks,wqs,bqs):
        self.wks=wks
        self.bks=bks
        self.wqs=wqs
        self.bqs=bqs
class Move:
    rankstoRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in rankstoRows.items()}
    filesToColumn = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    columnsToFiles = {v: k for k, v in filesToColumn.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove=False,isCastleMove=False):
        self.startRow=startSq[0]
        self.startColumn=startSq[1]
        self.endRow=endSq[0]
        self.endColumn=endSq[1]
        self.pieceMoved=board[self.startRow][self.startColumn]
        self.pieceCaptured=board[self.endRow][self.endColumn]
        self.id=self.id = self.startRow * 1000 + self.startColumn * 100 + self.endRow * 10 + self.endColumn
        self.isPawnPromotion = False
        if self.pieceMoved=="wp" and self.endRow==0:
            self.isPawnPromotion=True
        elif self.pieceMoved=="bp" and self.endRow==7:
            self.isPawnPromotion=True
        self.isEnpassantMove=isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured="wp" if self.pieceMoved=="bp" else "bp"
        self.isCastleMove=isCastleMove
    #Overiding equal method
    def __eq__(self, other):
        if(isinstance(other,Move)):
            return self.id==other.id
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow,self.startColumn)+ self.getRankFile(self.endRow,self.endColumn)
    def getRankFile(self,r,c):
        return self.columnsToFiles[c]+self.rowsToRanks[r]
