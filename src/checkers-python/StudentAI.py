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
        if len(move) != 0:
            self.board.make_move(move,self.opponent[self.color])
        else:
            self.color = 1

        move = self.minMaxSearch(self.board)
        self.board.make_move(move, self.color)

        return move
        # moves = self.board.get_all_possible_moves(self.color)
        # index = randint(0,len(moves)-1)
        # inner_index =  randint(0,len(moves[index])-1)
        # move = moves[index][inner_index]
        # self.board.make_move(move,self.color)       
        # return move

    def minMaxSearch(self, state):
        ourMoves = state.get_all_possible_moves(self.color)
        maxVal = float('-inf')
        for moves in ourMoves:
            for ourMove in moves:
                state.make_move(ourMove, self.color)
                tempMax = self.minValue(state)
                if maxVal < tempMax:
                    maxVal = tempMax
                    chosenMove = ourMove
                state.undo()

        return chosenMove
       
    def maxValue(self, state):
        self.depth += 1
        if(self.depth >= self.DEPTH_LIMIT):
            return self.evalFunction(state)
        ourMoves = state.get_all_possible_moves(self.color)
        maxVal = float('-inf')
        for moves in ourMoves:
            for ourMove in moves:
                state.make_move(ourMove, self.color)
                maxVal = max(maxVal, self.minValue(state))
                state.undo()
        return maxVal     

    
    def minValue(self, state):
        self.depth += 1
        if(self.depth >= self.DEPTH_LIMIT):
            return self.evalFunction(state)
        oppMoves = state.get_all_possible_moves(self.opponent[self.color])
        minVal = float('inf')
        for moves in oppMoves:
            for oppMove in moves:
                state.make_move(oppMove, self.opponent[self.color])
                minVal = min(minVal, self.maxValue(state))
                state.undo()
        return minVal  
    


    def evalFunction(self, state):
        ourCount = 0
        oppCount = 0
        for row in range(0, len(state.board)):
            for col in range(0, len(state.board[row])):
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
                    

                    
                

