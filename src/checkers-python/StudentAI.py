from random import randint
from BoardClasses import Move
from BoardClasses import Board
import asyncio
from enum import Enum


class TimeFlags(Enum):
    UNDER = 0
    OVER = 1


#The following part should be completed by students.
#Students can modify anything except the class name and exisiting functions and varibles.
class StudentAI():
    DEPTH_LIMIT = 2
    EARLY_GAME_TURNS = 10
    TURN_COLOR_MAP = {1 : "B", 2: "W"}

    def __init__(self,col,row,p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col,row,p)
        self.board.initialize_game()
        self.color = ''
        self.opponent = {1:2,2:1}
        self.color = 2
        self.depth = 0
        self.turn = 0
        self.control = asyncio.get_event_loop()
        self.time_left = TimeFlags.UNDER


    # After 20 seconds, will say that there is no more time
    async def timer(self, t):
        await asyncio.sleep(t)
        self.time_left = TimeFlags.OVER


    async def min_max_start(self):
        # Create tasks which will be ran concurrently
        time_limit = asyncio.Task(self.timer(20))
        minmax = asyncio.Task(self.minMaxSearch(self.board))

        # Run tasks together at the same time, returns minimax moves, hence [0]
        chosen_move = await asyncio.gather(minmax, time_limit)
        return chosen_move[0]


    def get_move(self,move):
        if len(move) != 0:
            self.board.make_move(move,self.opponent[self.color])
        else:
            self.color = 1
        self.turn += 1

        # Start the asynchronous minmax timer search
        move = self.control.run_until_complete(self.min_max_start())
        self.board.make_move(move, self.color)

        return move
        # moves = self.board.get_all_possible_moves(self.color)
        # index = randint(0,len(moves)-1)
        # inner_index =  randint(0,len(moves[index])-1)
        # move = moves[index][inner_index]
        # self.board.make_move(move,self.color)       
        # return move


    async def minMaxSearch(self, state):
        # Get all of our moves
        ourMoves = state.get_all_possible_moves(self.color)
        maxVal = float('-inf')
        # Iterate through all of our moves to find the max of them
        self.time_left = TimeFlags.UNDER
        while self.time_left != TimeFlags.OVER:
            for moves in ourMoves:
                for ourMove in moves:
                    state.make_move(ourMove, self.color)
                    tempMax = self.minValue(state, 1, float('-inf'), float('inf'))
                    if maxVal < tempMax:
                        maxVal = tempMax
                        chosenMove = ourMove
                    state.undo()

            self.DEPTH_LIMIT += 1
            await asyncio.sleep(1)
        
        # Return depth limit back to what it was originally
        self.DEPTH_LIMIT = 2
        return chosenMove


    def maxValue(self, state, depth, alpha, beta):
        #Check if this state is a win state
        isWin = state.is_win(self.TURN_COLOR_MAP[self.opponent[self.color]])
        if isWin != 0:
            if isWin == self.color:
                return 999999999
            elif isWin == self.opponent[self.color]:
                return -999999999

        #Get all of our moves and check if we have hit depth limit. If we have, run eval function
        ourMoves = state.get_all_possible_moves(self.color)
        if(depth >= self.DEPTH_LIMIT) or len(ourMoves) == 0:
            return self.evalFunction(state)
        
        v = float('-inf')
        depth += 1
        for moves in ourMoves:
            for ourMove in moves:
                state.make_move(ourMove, self.color)
                v = max(v, self.minValue(state, depth, alpha, beta))
                state.undo()
                if v >= beta:
                    return v
                alpha = max(alpha, v)
        return v     

    
    def minValue(self, state, depth, alpha, beta):
        isWin = state.is_win(self.TURN_COLOR_MAP[self.color])
        if isWin != 0:
            if isWin == self.color:
                return 999999999
            elif isWin == self.opponent[self.color]:
                return -999999999

        oppMoves = state.get_all_possible_moves(self.opponent[self.color])
        if(depth >= self.DEPTH_LIMIT) or len(oppMoves) == 0:
            return self.evalFunction(state)
        
        v = float('inf')
        depth += 1
        for moves in oppMoves:
            for oppMove in moves:
                state.make_move(oppMove, self.opponent[self.color])
                v = min(v, self.maxValue(state, depth, alpha, beta))
                state.undo()
                if v <= alpha:
                    return v
                beta = min(beta, v)
        return v  


    def evalFunction(self, state):
        if self.turn < self.EARLY_GAME_TURNS:
            return self.pieceAndRowEval(state)

        earlyLateList = self.getEarlyOrLate(state)
       
        if earlyLateList[0] == -1: #In this state, we have no pieces
            return -999999999

        if earlyLateList[0] == 1: # late game heuristic
            return self.lateGameKingEval(state, earlyLateList[1], earlyLateList[2])
        else: # Early game heuristic
            return self.pieceAndRowEval(state)


    def getEarlyOrLate(self, state):
        #return list of gameboard state [0 or 1 (early or lategame), ourKings, oppKings]
        #return 0 if early, or 1 if late
        totalCheckers = 0
        numOurCheckers = 0
        numOurKings = 0
        numOppCheckers = 0
        numOppKings = 0
        ourKings = []
        oppKings = []
        for row in range(0, len(state.board)):
            for col in range(0, len(state.board[row])):
                checkerPiece = state.board[row][col]

                if self.color == 1:
                    if checkerPiece.color == "B":
                        totalCheckers += 1
                        numOurCheckers += 1
                        if checkerPiece.is_king:
                            numOurKings += 1
                            ourKings.append((row, col))
                    elif checkerPiece.color == "W":
                        totalCheckers += 1
                        numOppCheckers += 1
                        if checkerPiece.is_king:
                            numOppKings += 1
                            oppKings.append((row, col))
                elif self.color == 2:
                    if checkerPiece.color == "W":
                        totalCheckers += 1
                        numOurCheckers += 1
                        if checkerPiece.is_king:
                            numOurKings += 1
                            ourKings.append((row, col))
                    elif checkerPiece.color == "B":
                        totalCheckers += 1
                        numOppCheckers += 1
                        if checkerPiece.is_king:
                            numOppKings += 1
                            oppKings.append((row, col))

        if numOurCheckers == 0:
            return [-1, ourKings, oppKings]                

        if numOurKings > numOppKings or numOurKings/numOurCheckers == 1:
            return [1, ourKings, oppKings]
        else:
            return [0, ourKings, oppKings]


    def lateGameKingEval(self, state, ourKings, oppKings):
        ourDistance = 0
        for ourKing in ourKings:
            for oppKing in oppKings:
                ourDistance += abs(ourKing[0] - oppKing[0]) + abs(ourKing[1] - oppKing[1])

        if len(ourKings) > len(oppKings): #attack
            return -1 * ourDistance
        else: #run away
            return ourDistance


    #black always starts from 0,0 while white starts on the other side
    def pieceAndRowEval(self, state):
        ourCount = 0
        oppCount = 0
        boardLen = len(state.board)
        for row in range(0, len(state.board)):
            for col in range(0, len(state.board[row])):
                checkerPiece = state.board[row][col]

                if self.color == 1:
                    if checkerPiece.color == "B": #our piece
                        if checkerPiece.is_king:
                            ourCount += 5 + (row + 1) + 2
                        else: #in our half
                            ourCount += 5 + (row + 1)
                        
                    elif checkerPiece.color == "W": #their piece
                        if checkerPiece.is_king:
                            oppCount += 5 + (boardLen - row) + 2
                        else:
                            oppCount += 5 + (boardLen - row)

                elif self.color == 2:
                    if checkerPiece.color == "W": #our piece
                        if checkerPiece.is_king:
                            ourCount += 5 + (boardLen - row) + 2
                        else:
                            ourCount += 5 + (boardLen - row)
                    elif checkerPiece.color == "B": #opponent piece
                        if checkerPiece.is_king:
                            oppCount += 5 + (row + 1) + 2
                        else:
                            oppCount += 5 + (row + 1)
        
        return ourCount - oppCount


    # #black always starts from 0,0 while white starts on the other side
    # def splitBoardEval(self, state):
    #     ourCount = 0
    #     oppCount = 0
    #     midRow = len(state.board)//2 
    #     for row in range(0, len(state.board)):
    #         for col in range(0, len(state.board[row])):
    #             checkerPiece = state.board[row][col]

    #             if self.color == 1:
    #                 if checkerPiece.color == "B": #our piece
    #                     if checkerPiece.is_king:
    #                         ourCount += 10
    #                     elif row < midRow: #in our half
    #                         ourCount += 5
    #                     elif row >= midRow: #in their half
    #                         ourCount += 7
    #                 elif checkerPiece.color == "W": #their piece
    #                     if checkerPiece.is_king:
    #                         oppCount += 10
    #                     elif row < midRow:
    #                         oppCount += 7
    #                     elif row >= midRow:
    #                         oppCount += 5
    #             elif self.color == 2:
    #                 if checkerPiece.color == "W": #our piece
    #                     if checkerPiece.is_king:
    #                         ourCount += 10
    #                     elif row < midRow: #we are in their half since they are now black
    #                         ourCount += 7
    #                     elif row >= midRow:
    #                         ourCount += 5
    #                 elif checkerPiece.color == "B": #opponent piece
    #                     if checkerPiece.is_king:
    #                         oppCount += 10
    #                     elif row < midRow: #they are in their own half
    #                         oppCount += 5
    #                     elif row >= midRow:
    #                         oppCount += 7
        
    #     return ourCount - oppCount
                        

    
    # def basicEval(self, state):
    #     ourCount = 0
    #     oppCount = 0
    #     for row in range(0, len(state.board)):
    #         for col in range(0, len(state.board[row])):
    #             checkerPiece = state.board[row][col]
               
    #            #We are first = Black checkers
    #             if self.color == 1:
    #                 if checkerPiece.color == "B":
    #                     if checkerPiece.is_king:
    #                         ourCount += 2
    #                     else:
    #                         ourCount += 1
    #                 elif checkerPiece.color == "W":
    #                     if checkerPiece.is_king:
    #                         oppCount += 2
    #                     else:
    #                         oppCount += 1
    #             elif self.color == 2: #We are second = White checkers
    #                 if checkerPiece.color == "W":
    #                     if checkerPiece.is_king:
    #                         ourCount += 2
    #                     else: 
    #                         ourCount += 1
    #                 elif checkerPiece.color == "B":
    #                     if checkerPiece.is_king:
    #                         oppCount += 2
    #                     else:
    #                         oppCount += 1

    #     return ourCount - oppCount
        
                # if checkerPiece.color == "B" and self.color == 1:
                #     if(checkerPiece.is_king):
                #         ourCount += 2
                #     else:
                #         ourCount += 1
                # elif checkerPiece.color == "W" and self.color == 1:
                #     if(checkerPiece.is_king):
                #         oppCount += 2
                #     else:
                #         oppCount += 1


                    

                    
                

