from random import randint
from BoardClasses import Move
from BoardClasses import Board
#The following part should be completed by students.
#Students can modify anything except the class name and exisiting functions and varibles.
class StudentAI():

    DEPTH_LIMIT = 3

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
    def get_move(self,move):
        return minMaxSearch(self.board)

         # if len(move) != 0:
        #     self.board.make_move(move,self.opponent[self.color])
        # else:
        #     self.color = 1
        # moves = self.board.get_all_possible_moves(self.color)
        # index = randint(0,len(moves)-1)
        # inner_index =  randint(0,len(moves[index])-1)
        # move = moves[index][inner_index]
        # self.board.make_move(move,self.color)       
        # return move

    def minMaxSearch(self, state):
        ourMoves = state.get_all_possible_moves(self.color)
        maxVal = float('-inf')
        for ourMove in ourMoves:
            state.make_move(ourMove, self.color)
            tempMax = minValue(state)
            if maxVal < tempMax:
                maxVal = tempMax
                chosenMove = ourMove
            state.undo()
        return chosenMove
       
    def maxValue(self, state):
        self.depth += 1
        if(depth >= DEPTH_LIMIT):
            evalFunction(state)
        ourMoves = state.get_all_possible_moves(self.color)
        maxVal = float('-inf')
        for ourMove in ourMoves:
            state.make_move(ourMove, self.color)
            maxVal = max(maxVal, self.maxValue(state))
            state.undo()
        return maxVal     

    
    def minValue(self, state):
        self.depth += 1
        if(depth >= DEPTH_LIMIT):
            evalFunction(state)
        oppMoves = state.get_all_possible_moves(self.opponent[self.color])
        minVal = float('inf')
        for oppMove in oppMoves:
            state.make_move(oppMove, self.opponent[self.color])
            minVal = min(minVal, self.minValue(state))
            state.undo()
        return minVal  
    


    def evalFunction(self, state):
        ourCount = 0
        oppCount = 0
        for row in state.board:
            for col in row:
                checkerPiece = state.board[row][col]
                if checkerPiece.color == "B" and self.color == 1:
                    if(checkerPiece.is_king):
                        ourCount += 2
                    else:
                        ourCount += 1
                elif checkerPiece.color == "W" and self.color != 1:
                    if(checkerPiece.is_king):
                        oppCount += 2
                    else:
                        oppCount += 1

        return ourCount - oppCount
                    

                    
                

