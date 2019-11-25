from random import randint
from BoardClasses import Move
from BoardClasses import Board
import asyncio
from enum import Enum
import time


class TimeFlags(Enum):
    UNDER = 0
    OVER = 1

#The following part should be completed by students.
#Students can modify anything except the class name and exisiting functions and varibles.
class StudentAI():
    INITIAL_DEPTH_LIMIT = 5
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
        self.iterative_depth_limit = self.INITIAL_DEPTH_LIMIT
        self.time_left = TimeFlags.UNDER
        self.time_used = 0
        self.upper_depth_limit = float('inf')
        self.time_limit = 480       # 8 minutes


    # Timer, which can to have set values based on total used time. Min sleep must be > 1
    async def timer(self, state):
        # Here was originally a hueristic to determin which sleep pattern/upper depth limit to use
        # our_count = self.countOurPieces(state)
        # if self.time_used < 120:          # Use this sleep before two minute mark
        #     if our_count <= self.p*self.row/2*0.4:
        #         self.upper_depth_limit = 12
        #         await asyncio.sleep(20)
        #     else:
        #         self.upper_depth_limit = 2
        #         await asyncio.sleep(1)
        
        try:
            if self.time_used < 120:          # Use this sleep before two minute mark
                self.upper_depth_limit = 8
                await asyncio.sleep(15)
            
            elif self.time_used < 240:          # Four minute mark
                self.upper_depth_limit = 7
                await asyncio.sleep(10)
        
            elif self.time_used < 360:          # Six minute mark
                self.upper_depth_limit = 7
                await asyncio.sleep(8)
            
            elif self.time_used < 420:          # Seven minute mark
                self.upper_depth_limit = 6
                await asyncio.sleep(5)
            
            else:                               # Anything longer than above
                self.upper_depth_limit = 5
                await asyncio.sleep(1)
            
            # After waiting, set time to over time
            self.time_left = TimeFlags.OVER
        
        # Handle when we cancel the timer
        except asyncio.CancelledError:
            self.time_left = TimeFlags.UNDER
        
        # finally:
        #     self.upper_depth_limit = float('inf')


    # Asyncio function that will create the tasks and run them concurrently
    # It will wait until both are either finished or canceled, and then return that move
    async def min_max_start(self):
        # Create tasks which will be ran concurrently
        self.task_timer = asyncio.Task(self.timer(self.board))
        self.task_minmax = asyncio.Task(self.minMaxSearch(self.board))

        # Run tasks together at the same time, returns minimax moves, hence [0]
        chosen_move = await asyncio.gather(self.task_minmax, self.task_timer)
        return chosen_move[0]


    def get_move(self,move):
        # Keep track of time so we can figure out total time used
        start_time = self.control.time()
        
        if len(move) != 0:
            self.board.make_move(move,self.opponent[self.color])
        else:
            self.color = 1
        self.turn += 1

        # Start the asynchronous minmax timer search
        move = self.control.run_until_complete(self.min_max_start())
        
        # Make our move
        self.board.make_move(move, self.color)

        # Add to our ongoing used time, 8 minute time limit as defined under self.timer()
        self.time_used += self.control.time() - start_time
        
        return move


    async def minMaxSearch(self, state):
        # Get all of our moves
        ourMoves = state.get_all_possible_moves(self.color)
        maxVal = float('-inf')
        lastBestVal = float('-inf')
        
        # Iterate through all of our moves to find the max of them
        self.time_left = TimeFlags.UNDER
        self.iterative_depth_limit = self.INITIAL_DEPTH_LIMIT
        while self.time_left != TimeFlags.OVER:
            for moves in ourMoves:
                for ourMove in moves:
                    state.make_move(ourMove, self.color)
                    tempMax = await self.minValue(state, 1, float('-inf'), float('inf'))
                    if maxVal < tempMax:
                        maxVal = tempMax
                        chosenMove = ourMove
                        
                        # If maxVal is better than the one kept from the lastBestMove, set those as lastBest
                        if lastBestVal < maxVal:
                            lastBestVal = maxVal
                            lastBestMove = chosenMove
                    
                    # If we're over time, just return our current best
                    if self.time_left == TimeFlags.OVER:
                        return lastBestMove
                    
                    state.undo()
            
            
            
            # Upon each iteration, increase depth limit by 1
            self.iterative_depth_limit += 1
           
            # If we reached out set max, stop iterating and just return what we have
            if self.iterative_depth_limit > self.upper_depth_limit:
                break
            
            # Context switch back to the timer, to check if it's ran out
            await asyncio.sleep(0)
        
        # Return depth limit back to what it was originally, cancel the timer because we've reached
        # the upper depth limit.
        self.iterative_depth_limit = self.INITIAL_DEPTH_LIMIT
        self.task_timer.cancel()
        
        return lastBestMove


    async def maxValue(self, state, depth, alpha, beta):
        #Check if this state is a win state
        isWin = state.is_win(self.TURN_COLOR_MAP[self.opponent[self.color]])
        if isWin != 0:
            if isWin == self.color:
                return 999999999
            elif isWin == self.opponent[self.color]:
                return -999999999
        await asyncio.sleep(0)
        #Get all of our moves and check if we have hit depth limit or if timer runs out. If we have, run eval function
        ourMoves = state.get_all_possible_moves(self.color)
        if(depth >= self.iterative_depth_limit) or len(ourMoves) == 0 or self.time_left == TimeFlags.OVER:
            return self.evalFunction(state)
        
        v = float('-inf')
        depth += 1
        for moves in ourMoves:
            for ourMove in moves:
                state.make_move(ourMove, self.color)
                v = max(v, await self.minValue(state, depth, alpha, beta))
                state.undo()
                if v >= beta:
                    return v
                alpha = max(alpha, v)
        return v     

    
    async def minValue(self, state, depth, alpha, beta):
        isWin = state.is_win(self.TURN_COLOR_MAP[self.color])
        if isWin != 0:
            if isWin == self.color:
                return 999999999
            elif isWin == self.opponent[self.color]:
                return -999999999
        await asyncio.sleep(0)
        oppMoves = state.get_all_possible_moves(self.opponent[self.color])
        if(depth >= self.iterative_depth_limit) or len(oppMoves) == 0 or self.time_left == TimeFlags.OVER:
            return self.evalFunction(state)
        
        v = float('inf')
        depth += 1
        for moves in oppMoves:
            for oppMove in moves:
                state.make_move(oppMove, self.opponent[self.color])
                v = min(v, await self.maxValue(state, depth, alpha, beta))
                state.undo()
                if v <= alpha:
                    return v
                beta = min(beta, v)
        return v  


    def evalFunction(self, state):
        return self.ieeeEvaluation(state)


    def countOurPieces(self, state):
        ongoing = 0
        for row in range(0, len(state.board)):
            for col in range(0, len(state.board[row])):
                checkerPiece = state.board[row][col]
                
                if self.color == 1:
                    if checkerPiece.color == "B":
                        ongoing += 1
                elif self.color == 2:
                    if checkerPiece.color == "W":
                        ongoing += 1
        return ongoing


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


    #black always starts from 0,0 while white starts on the other side
    def ieeeEvaluation(self, state):
        ourPawn = 0
        ourKing = 0
        ourMiddle = 0
        ourRow = 0
        oppPawn = 0
        oppKing = 0
        oppMiddle = 0
        oppRow = 0
        boardRowLen = len(state.board)
        middleRowEnd = len(state.board) - 3
        middleColEnd = len(state.board[0]) - 3
        for row in range(0, len(state.board)):
            for col in range(0, len(state.board[row])):
                checkerPiece = state.board[row][col]

                if self.color == 1:
                    if checkerPiece.color == "B": #our piece
                        ourRow += row
                        if row >= 2 and row <= middleRowEnd and col >= 2 and col <= middleColEnd:
                            ourMiddle += 1 

                        if checkerPiece.is_king:
                            ourKing += 1
                        else: 
                            ourPawn += 1
                        
                    elif checkerPiece.color == "W": #their piece
                        oppRow += boardRowLen - row - 1
                        if row >= 2 and row <= middleRowEnd and col >= 2 and col <= middleColEnd:
                            oppMiddle += 1

                        if checkerPiece.is_king:
                            oppKing += 1
                        else:
                            oppPawn += 1
                elif self.color == 2:
                    if checkerPiece.color == "W": #our piece
                        ourRow += boardRowLen - row - 1
                        if row >= 2 and row <= middleRowEnd and col >= 2 and col <= middleColEnd:
                            ourMiddle += 1

                        if checkerPiece.is_king:
                            ourKing += 1
                        else:
                            ourPawn += 1
                    elif checkerPiece.color == "B": #opponent piece
                        oppRow += row
                        if row >= 2 and row <= middleRowEnd and col >= 2 and col <= middleColEnd:
                            oppMiddle += 1

                        if checkerPiece.is_king:
                            oppKing += 1
                        else:
                            oppPawn += 1
        
        return (80 * ( (ourPawn - oppPawn) + 2.5 * (ourKing - oppKing) )) + (40 * (ourRow - oppRow)) + (20 * (ourMiddle - oppMiddle)) 