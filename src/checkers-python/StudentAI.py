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
        self.late_game_flag = False
        self.heuristic_flag = 1 #use ieee1, if 2, use ieee2
        self.flag_just_changed = 0

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
        lastBestVal = float('-inf')
        
        # Iterate through all of our moves to find the max of them
        self.time_left = TimeFlags.UNDER
        self.iterative_depth_limit = self.INITIAL_DEPTH_LIMIT
        while self.time_left != TimeFlags.OVER:
            for moves in ourMoves:
                for ourMove in moves:
                    # If we're over time, just return our current best
                    if self.time_left == TimeFlags.OVER:
                        return lastBestMove
                    
                    state.make_move(ourMove, self.color)
                    tempMax = await self.minValue(state, 1, float('-inf'), float('inf'))
                    if lastBestVal < tempMax:
                        lastBestVal = tempMax
                        lastBestMove = ourMove
                    
                    state.undo()
            
            # If maxVal is better than the one kept from the lastBestMove, set those as lastBest
            
            
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
        if self.turn < self.EARLY_GAME_TURNS:
            return self.ieeeEvaluation1(state) #go to their side

        if self.late_game_flag:
            if self.flag_just_changed > 0:
                self.flag_just_changed -= 1
                if self.heuristic_flag == 1:
                    return self.ieeeEvaluation1(state)
                elif self.heuristic_flag == 2:
                    return self.ieeeEvaluation2(state)
            else:
                self.checkSide(state)
                if self.heuristic_flag == 1:
                    return self.ieeeEvaluation1(state)
                elif self.heuristic_flag == 2:
                    return self.ieeeEvaluation2(state)

        else:
            self.checkLateGame(state)
            return self.ieeeEvaluation1(state)

        # earlyOrLate = self.getEarlyOrLate(state)
        # if earlyOrLate[0] == -1:
        #     return -999999999
        # elif earlyOrLate[0] == 0:
        #     return self.ieeeEvaluation(state)
        # elif earlyOrLate[0] == 1:
        #     return self.lateGameKingEval(state, earlyOrLate[1], earlyOrLate[2], earlyOrLate[3]) 

    def checkLateGame(self, state):
        numOurCheckers = 0
        numOurKings = 0
        for row in range(0, len(state.board)):
            for col in range(0, len(state.board[row])):
                checkerPiece = state.board[row][col]

                if self.color == 1:
                    if checkerPiece.color == "B":
                        numOurCheckers += 1
                        if checkerPiece.is_king:
                            numOurKings += 1

                elif self.color == 2:
                    if checkerPiece.color == "W":
                        numOurCheckers += 1
                        if checkerPiece.is_king:
                            numOurKings += 1
        
        if numOurKings/numOurCheckers == 1:
            self.late_game_flag = True


    def checkSide(self, state):
        #return 0 if we have our troops not yet all on their side
        #return 1 if we have our troops on their side 
        numOurCheckers = 0
        numSideUs = 0 
        numSideTheirs = 0
        if self.color == 1:
            rowCheck = 2 if len(state.board) == 7 else 3 
            rowCheckTheir = 4
        elif self.color == 2:
            rowCheck = 4
            rowCheckTheir = 2 if len(state.board) == 7 else 3

        for row in range(0, len(state.board)):
            for col in range(0, len(state.board[row])):
                checkerPiece = state.board[row][col]

                if self.color == 1:
                    if checkerPiece.color == "B":
                        numOurCheckers += 1
                        if row < rowCheck:
                            numSideUs += 1
                        if row > rowCheckTheir:
                            numSideTheirs += 1
                            
                elif self.color == 2:
                    if checkerPiece.color == "W":
                        numOurCheckers += 1
                        if row > rowCheck:
                            numSideUs += 1
                        if row < rowCheckTheir:
                            numSideTheirs += 1
                    
        if self.heuristic_flag == 1 and numSideTheirs/numOurCheckers > 0.8:
            self.heuristic_flag = 2
            self.flag_just_changed = 10
        
        if self.heuristic_flag == 2 and numSideUs/numOurCheckers > 0.8:
            self.heuristic_flag = 1
            self.flag_just_changed = 10

    #black always starts from 0,0 while white starts on the other side
    def ieeeEvaluation1(self, state):
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

    def ieeeEvaluation2(self, state):
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
                        ourRow += boardRowLen - row - 1
                        if row >= 2 and row <= middleRowEnd and col >= 2 and col <= middleColEnd:
                            ourMiddle += 1 

                        if checkerPiece.is_king:
                            ourKing += 1
                        else: 
                            ourPawn += 1
                        
                    elif checkerPiece.color == "W": #their piece
                        oppRow += row
                        if row >= 2 and row <= middleRowEnd and col >= 2 and col <= middleColEnd:
                            oppMiddle += 1

                        if checkerPiece.is_king:
                            oppKing += 1
                        else:
                            oppPawn += 1
                elif self.color == 2:
                    if checkerPiece.color == "W": #our piece
                        ourRow += row
                        if row >= 2 and row <= middleRowEnd and col >= 2 and col <= middleColEnd:
                            ourMiddle += 1

                        if checkerPiece.is_king:
                            ourKing += 1
                        else:
                            ourPawn += 1
                    elif checkerPiece.color == "B": #opponent piece
                        oppRow += boardRowLen - row - 1
                        if row >= 2 and row <= middleRowEnd and col >= 2 and col <= middleColEnd:
                            oppMiddle += 1

                        if checkerPiece.is_king:
                            oppKing += 1
                        else:
                            oppPawn += 1
        
        return (80 * ( (ourPawn - oppPawn) + 2.5 * (ourKing - oppKing) )) + (40 * (ourRow - oppRow)) + (20 * (ourMiddle - oppMiddle)) 

    # def lateGameKingEval(self, state, ourKings, oppKings, oppPawns):
    #     ourDistance = 0
    #     numOurKings = len(ourKings)
    #     numOppKings = len(oppKings)
    #     numOppPawns = len(oppPawns)
    #     for ourKing in ourKings:
    #         for oppKing in oppKings:
    #             checkersDistance = max(abs(ourKing[0] - oppKing[0]), abs(ourKing[1] - oppKing[1]))
    #             ourDistance += checkersDistance
    #         for oppPawn in oppPawns:
    #             checkersDistance = max(abs(ourKing[0] - oppPawn[0]), abs(ourKing[1] - oppPawn[1]))
    #             ourDistance += checkersDistance


    #     if len(ourKings) > len(oppKings): #attack
    #         return (1000 * ( 2.5 * (numOurKings - numOppKings) - numOppPawns ) ) + round((1/ourDistance) * 100)
    #     else: #run away
    #         return (1000 * ( 2.5 * (numOurKings - numOppKings) - numOppPawns ) ) + 40 * ourDistance


    # def getEarlyOrLate(self, state):
    #     #return list of gameboard state [0 or 1 (early or lategame), ourKings, oppKings]
    #     #return 0 if early, or 1 if late
    #     numOurCheckers = 0
    #     numOurKings = 0
    #     ourKings = []
    #     oppKings = []
    #     oppPawns = []
    #     for row in range(0, len(state.board)):
    #         for col in range(0, len(state.board[row])):
    #             checkerPiece = state.board[row][col]

    #             if self.color == 1:
    #                 if checkerPiece.color == "B":
    #                     numOurCheckers += 1
    #                     if checkerPiece.is_king:
    #                         numOurKings += 1
    #                         ourKings.append((row, col))
    #                 elif checkerPiece.color == "W":
    #                     if checkerPiece.is_king:
    #                         oppKings.append((row, col))
    #                     else:
    #                         oppPawns.append((row, col))
    #             elif self.color == 2:
    #                 if checkerPiece.color == "W":
    #                     numOurCheckers += 1
    #                     if checkerPiece.is_king:
    #                         numOurKings += 1
    #                         ourKings.append((row, col))
    #                 elif checkerPiece.color == "B":
    #                     if checkerPiece.is_king:
    #                         oppKings.append((row, col))
    #                     else:
    #                         oppPawns.append((row, col))

    #     if numOurCheckers == 0:
    #         return [-1, ourKings, oppKings, oppPawns]                

    #     if numOurKings/numOurCheckers == 1:
    #         return [1, ourKings, oppKings, oppPawns]
    #     else:
    #         return [0, ourKings, oppKings, oppPawns]


    # def countOurPieces(self, state):
    #     ongoing = 0
    #     for row in range(0, len(state.board)):
    #         for col in range(0, len(state.board[row])):
    #             checkerPiece = state.board[row][col]
                
    #             if self.color == 1:
    #                 if checkerPiece.color == "B":
    #                     ongoing += 1
    #             elif self.color == 2:
    #                 if checkerPiece.color == "W":
    #                     ongoing += 1
    #     return ongoing

    # #black always starts from 0,0 while white starts on the other side
    # def pieceAndRowEval(self, state):
    #     ourCount = 0
    #     oppCount = 0
    #     boardLen = len(state.board)
    #     for row in range(0, len(state.board)):
    #         for col in range(0, len(state.board[row])):
    #             checkerPiece = state.board[row][col]

    #             if self.color == 1:
    #                 if checkerPiece.color == "B": #our piece
    #                     if checkerPiece.is_king:
    #                         ourCount += 5 + (row + 1) + 2
    #                     else: #in our half
    #                         ourCount += 5 + (row + 1)
                        
    #                 elif checkerPiece.color == "W": #their piece
    #                     if checkerPiece.is_king:
    #                         oppCount += 5 + (boardLen - row) + 2
    #                     else:
    #                         oppCount += 5 + (boardLen - row)

    #             elif self.color == 2:
    #                 if checkerPiece.color == "W": #our piece
    #                     if checkerPiece.is_king:
    #                         ourCount += 5 + (boardLen - row) + 2
    #                     else:
    #                         ourCount += 5 + (boardLen - row)
    #                 elif checkerPiece.color == "B": #opponent piece
    #                     if checkerPiece.is_king:
    #                         oppCount += 5 + (row + 1) + 2
    #                     else:
    #                         oppCount += 5 + (row + 1)
        
    #     return ourCount - oppCount


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