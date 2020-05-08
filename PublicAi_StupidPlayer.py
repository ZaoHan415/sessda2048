import random

class Player:
    def __init__(self, isFirst, array):
        # 初始化
        self.isFirst = isFirst
        self.array = array
    def output(self, currentRound, board, mode):
        if mode == 'position':
            if board.getNext(self.isFirst, currentRound):
                return board.getNext(self.isFirst, currentRound)
            else:
                alist = board.getNone(not self.isFirst)
                return alist[random.randint(0, len(alist)-1)]
        else:
            directionList = [2, 3, 0, 1] if self.isFirst else [3, 2, 1, 0]
            for direction in directionList:
                if board.move(self.isFirst, direction): return direction