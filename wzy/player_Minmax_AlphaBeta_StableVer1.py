# 基础版minmax 算法
# 创建于2020年5月8日 by Czarja
# 添加αβ剪枝，2020 5 09 by DXLi
import numpy


class Player:
    def __init__(self, isFirst, array):
        # 初始化
        self.isFirst = isFirst
        self.array = array
        self.maxValue = 2E9
        # self.weight = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096]
        self.weight = [1, 2, 4, 8, 16, 32, 64, 128, 259, 519, 1039, 2079, 4159]
        # self.weight = [1, 2, 5, 11, 23, 47, 95, 191, 383, 767, 1535, 3071, 6143]
        # self.weight = [1, 3, 7, 15, 31, 63, 127, 255, 511, 1023, 2047, 4095, 8191]
        self.maxRounds = len(array)
        self.totalTime = 5

    @staticmethod
    def cannotMove(belong, board):  # 如果某方无路可走返回True
        for direction in [0, 1, 2, 3]:
            if board.move(belong, direction):
                return False
        return True

    # 不会修改board，只是针对position情况返回所有可以下棋的位置列表
    @staticmethod
    def getActions(currentRound, board, mode, peer):
        if mode == 'position':
            ownSidePos = board.getNext(peer, currentRound)
            otherSidePos = board.getNone(not peer)
            if len(ownSidePos) == 2:
                otherSidePos.insert(0,ownSidePos)
            return otherSidePos
        else:
            return [0, 1, 2, 3]

    def weightSum(self, lst): 
        return sum(map(self.weight.__getitem__, lst))

    def score(self, board):  # 最简单的局面估值函数
        # 目前完全是玄学估值
        myScoreLst = board.getScore(self.isFirst)
        RivalScoreLst = board.getScore(not self.isFirst)
        #根据先后手修改数值分配
        tf=2
        tnf=2
        lst1=[(0,4),(1,4),(2,4),(3,4)]
        lst2=[(0,3),(1,3),(2,3),(3,3)]
        if self.isFirst:
            total = self.weightSum(myScoreLst) - self.weightSum(RivalScoreLst)/tf
            for item in lst1:
                if board.getBelong(item):
                    total+=self.weight[board.getValue(item)]
            
        else:
            total = self.weightSum(myScoreLst) - self.weightSum(RivalScoreLst)/tnf
            for item in lst2:
                if board.getBelong(item):
                    total-=self.weight[board.getValue(item)]   
        '''
        # 修改了空位函数，使得剩的格子越少空位越值钱，根据己方所剩棋子的最大值计算空位值
        k1=len(board.getNone(self.isFirst))
        if k1<=9:
            total-=2**(9-k1)
        '''
        #total += len(board.getNone(self.isFirst))*1.5
        # 无路可走的情况要避免
        # if Player.cannotMove(self.isFirst, board):
        #     return -self.maxValue
        # elif Player.cannotMove(not self.isFirst, board):
        #     return self.maxValue
        # else:
        return total

    def _minMaxRecur(self, board, depth, phase, currentRound, inc, alpha=-(2E9), beta=+(2E9)):
        # 返回值为局面估值
        if depth <= 0 or currentRound >= self.maxRounds:
            return self.score(board)
        peer = not bool(phase % 2)
        flag = bool(peer == self.isFirst)
        # flag = peer
        # flag = True时为自己回合，peer = True的时候为先手方回合
        if currentRound > self.maxRounds * 0.6:  # 更新了，0.6待调整
            tLeft = board.getTime(self.isFirst)
            if (self.totalTime - tLeft) * self.maxRounds / currentRound > self.totalTime:
                depth -= 1
        if phase == 2 or phase == 3:
            if phase == 3:
                currentRound += 1
            for d in [0, 1, 2, 3]:
                newBoard = board.copy()
                if newBoard.move(peer, d):
                    curScore = self._minMaxRecur(newBoard, depth - 1, (phase + 1) % 4, currentRound, inc, alpha, beta)
                    if not flag and (curScore < beta):
                        beta = curScore
                        if alpha >= beta:
                            return alpha
                    elif flag and (curScore > alpha):
                        alpha = curScore
                        if alpha >= beta:
                            return beta
        else:
            posLst = Player.getActions(currentRound, board, 'position', peer)
            posLstLen = len(posLst)
            if posLstLen <= 5:
                if inc < 4:
                    depth += 1
                    inc += 1
                for pos in posLst:
                    newBoard = board.copy()
                    newBoard.add(peer, pos)
                    curScore = self._minMaxRecur(newBoard, depth-1, phase + 1, currentRound, inc, alpha, beta)
                    if not flag and (curScore < beta):
                        beta = curScore
                        if alpha >= beta:
                            return alpha
                    elif flag and (curScore > alpha):
                        alpha = curScore
                        if alpha >= beta:
                            return beta
            else:
                newBoard = board.copy()
                newBoard.add(peer, posLst[-1])
                curScore = self._minMaxRecur(newBoard, depth-1, phase + 1, currentRound, inc, alpha, beta)
                return curScore
        return alpha if flag else beta

    def minmaxDecisionF(self, board, currentRound, mode):  # 针对先手进攻局
        actions = Player.getActions(currentRound, board, mode, self.isFirst)
        choice = None
        finalScore = -self.maxValue
        if mode[0] == '_':
            return None
        if mode == 'direction':
            # phase 0 1 2 3
            phase = 2
            depth = 3
            for d in actions:
                newBoard = board.copy()
                if newBoard.move(self.isFirst, d):
                    curScore = self._minMaxRecur(newBoard, depth, (phase+1) % 4, currentRound, 0)
                    if curScore >= finalScore:  # 所有情况搞一个列表，选出分值最高的
                        finalScore = curScore
                        choice = d
        else:
            phase = 0
            if len(actions) > 5 and board.getNext(self.isFirst, currentRound):  # 待调整
                return board.getNext(self.isFirst, currentRound)
            else:
                depth = 3
                for pos in actions:
                    newBoard = board.copy()
                    newBoard.add(self.isFirst, pos)
                    curScore = self._minMaxRecur(newBoard, depth, phase + 1, currentRound, 0)
                    if curScore >= finalScore:
                        finalScore = curScore
                        choice = pos
        return choice

    def minmaxDecisionNF(self, board, currentRound, mode):
        actions = Player.getActions(currentRound, board, mode, self.isFirst)
        choice = None
        finalScore = -self.maxValue
        if mode[0] == '_':
            return None
        if mode == 'direction':
            # phase 0 1 2 3
            phase = 3
            depth = 3
            for d in actions:
                newBoard = board.copy()
                if newBoard.move(self.isFirst, d):
                    curScore = self._minMaxRecur(newBoard, depth, (phase + 1) % 4, currentRound + 1, 1)
                    if curScore >= finalScore:  # 所有情况搞一个列表，选出分值最高的
                        finalScore = curScore
                        choice = d
        else:
            phase = 1
            if len(actions) > 5 and board.getNext(self.isFirst, currentRound):  # 待调整
                return board.getNext(self.isFirst, currentRound)
            else:
                depth = 2
                for pos in actions:
                    newBoard = board.copy()
                    newBoard.add(self.isFirst, pos)
                    curScore = self._minMaxRecur(newBoard, depth, phase + 1, currentRound, 0)
                    if curScore >= finalScore:
                        finalScore = curScore
                        choice = pos
        return choice

    def output(self, currentRound, board, mode):
        if self.isFirst:
            return self.minmaxDecisionF(board, currentRound, mode)
        else:
            return self.minmaxDecisionNF(board, currentRound, mode)


# if __name__ == '__main__':
#     a = Player(True, [])
#     print(a.weightSum([1, 4]))
