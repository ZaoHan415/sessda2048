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
        # self.weight = [1, 2, 4, 8, 16, 32, 64, 128, 259, 519, 1039, 2079, 4159]
        self.weight = [4**i for i in range(13)]
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
                otherSidePos.insert(0, ownSidePos)
            return otherSidePos
        else:
            return [0, 1, 2, 3]

    def weightSum(self, lst):  # 平方和作为总分
        return sum(map(self.weight.__getitem__, lst))

    def score(self, board):  # 最简单的局面估值函数
        # 目前完全是玄学估值
        myScoreLst = board.getScore(self.isFirst)
        if self.isFirst:
            total = self.weightSum(myScoreLst)
        else:
            RivalScoreLst = board.getScore(not self.isFirst)
            total = self.weightSum(myScoreLst) - self.weightSum(RivalScoreLst)/1.5
        # total += self.weight[myScoreLst[-1]]*4
        # total -= self.weight[RivalScoreLst[-1]]*4
        # 一个空位价值1.5分
        #total += len(board.getNone(self.isFirst))*1.5
        #鼓励贴边
        #lst=[(0,4),(1,4),(2,4),(3,4),(0,3),(1,3),(2,3),(3,3)]
        #total = self.weightSum(myScoreLst) - self.weightSum(RivalScoreLst)/2
        #for item in lst:
         #   if board.getBelong(item):
          #      total+=self.weight[board.getValue(item)]/4
        # 无路可走的情况要避免
        # if Player.cannotMove(self.isFirst, board):
            # return -self.maxValue
        # elif Player.cannotMove(not self.isFirst, board):
            # return self.maxValue
        # else:
        return total

    def _minMaxRecurF(self, board, depth, phase, currentRound, inc, alpha=-(2E9), beta=+(2E9)):
        # 返回值为局面估值
        if depth <= 0 or currentRound >= self.maxRounds:
            return self.score(board)
        peer = not bool(phase % 2)
        flag = bool(peer == self.isFirst)
        # flag = peer
        # flag = True时为自己回合，peer = True的时候为先手方回合
        if currentRound > self.maxRounds * 0.58:  # 更新了，0.6待调整
            tLeft = board.getTime(self.isFirst)
            if (self.totalTime - tLeft) * self.maxRounds / currentRound > self.totalTime:
                depth -= 1
                if currentRound > self.maxRounds * 0.9:
                    depth -= 1
                    if currentRound > self.maxRounds * 0.95:
                        depth -= 1
                        if currentRound >= self.maxRounds - 10:
                            depth = -5
        if phase == 2 or phase == 3:
            if phase == 3:
                currentRound += 1
            for d in [3,0,1,2]:
                newBoard = board.copy()
                if newBoard.move(peer, d):
                    curScore = self._minMaxRecurF(newBoard, depth - 1, (phase + 1) % 4, currentRound, inc, alpha, beta)
                    if not flag and (curScore < beta):
                        beta = curScore
                        if alpha >= beta:
                            return alpha
                    elif flag and (curScore > alpha):
                        alpha = curScore
                        if alpha >= beta:
                            return beta
        else:
            posLst = self.getActions(currentRound, board, 'position', peer)
            posLstLen = len(posLst)
            if len(board.getNext(peer, currentRound)) == 0:
                curScore = self._minMaxRecurF(board, depth-1, phase + 1, currentRound, inc, alpha, beta)
                if not flag and (curScore < beta):
                    beta = curScore
                    if alpha >= beta:
                        return alpha
                elif flag and (curScore > alpha):
                    alpha = curScore
                    if alpha >= beta:
                        return beta
            elif posLstLen <= 5 and currentRound > 0.4*self.maxRounds:
            # elif posLstLen <= 5:
                if inc < 4:
                    depth += 1
                    inc += 1
                for pos in posLst:
                    newBoard = board.copy()
                    newBoard.add(peer, pos)
                    curScore = self._minMaxRecurF(newBoard, depth-1, phase + 1, currentRound, inc, alpha, beta)
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
                newBoard.add(peer, posLst[0])
                curScore = self._minMaxRecurF(newBoard, depth-1, phase + 1, currentRound, inc, alpha, beta)
                return curScore
        return alpha if flag else beta

    def _minMaxRecurNF(self, board, depth, phase, currentRound, inc, alpha=-(2E9), beta=+(2E9)):
        # 返回值为局面估值
        if depth <= 0 or currentRound >= self.maxRounds:
            return self.score(board)
        peer = not bool(phase % 2)
        flag = bool(peer == self.isFirst)
        # flag != peer
        # flag = True时为自己回合，peer = True的时候为先手方回合
        if currentRound > self.maxRounds * 0.65:  # 更新了，0.6待调整
            tLeft = board.getTime(self.isFirst)
            if (self.totalTime - tLeft) * self.maxRounds / currentRound > self.totalTime:
                depth -= 1
                if currentRound > self.maxRounds * 0.9:
                    depth -= 1
                    if currentRound > self.maxRounds * 0.95:
                        depth -= 1
                        if currentRound >= self.maxRounds - 10:
                            depth = -5
        if phase == 2 or phase == 3:
            if phase == 3:
                currentRound += 1
            for d in [2,0,1,3]:
                newBoard = board.copy()
                if newBoard.move(peer, d):
                    curScore = self._minMaxRecurNF(newBoard, depth - 1, (phase + 1) % 4, currentRound, inc, alpha, beta)
                    if not flag and (curScore < beta):
                        beta = curScore
                        if alpha >= beta:
                            return alpha
                    elif flag and (curScore > alpha):
                        alpha = curScore
                        if alpha >= beta:
                            return beta
        else:
            posLst = self.getActions(currentRound, board, 'position', peer)
            posLstLen = len(posLst)
            if len(board.getNext(peer, currentRound)) == 0:
                curScore = self._minMaxRecurF(board, depth-1, phase + 1, currentRound, inc, alpha, beta)
                if not flag and (curScore < beta):
                    beta = curScore
                    if alpha >= beta:
                        return alpha
                elif flag and (curScore > alpha):
                    alpha = curScore
                    if alpha >= beta:
                        return beta
            elif posLstLen <= 5 and currentRound > 0.4*self.maxRounds:
            # elif posLstLen <= 5:
                if inc < 4:
                    depth += 1
                    inc += 1
                for pos in posLst:
                    newBoard = board.copy()
                    newBoard.add(peer, pos)
                    curScore = self._minMaxRecurNF(newBoard, depth-1, phase + 1, currentRound, inc, alpha, beta)
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
                newBoard.add(peer, posLst[0])
                curScore = self._minMaxRecurNF(newBoard, depth-1, phase + 1, currentRound, inc, alpha, beta)
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
            depth = 6
            for d in [3,0,1,2]:
                newBoard = board.copy()
                if newBoard.move(self.isFirst, d):
                    curScore = self._minMaxRecurF(newBoard, depth, (phase+1) % 4, currentRound, 1)
                    if curScore >= finalScore:  # 所有情况搞一个列表，选出分值最高的
                        finalScore = curScore
                        choice = d
        else:
            phase = 0
            if len(actions) > 5 or currentRound <= 0.4*self.maxRounds:  # 待调整
            # if len(actions) > 5:
                return actions[0]
            else:
                depth = 4
                for pos in actions:
                    newBoard = board.copy()
                    newBoard.add(self.isFirst, pos)
                    curScore = self._minMaxRecurF(newBoard, depth, phase + 1, currentRound, 0)
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
            depth = 6
            for d in [2,0,1,3]:
                newBoard = board.copy()
                if newBoard.move(self.isFirst, d):
                    curScore = self._minMaxRecurNF(newBoard, depth, (phase + 1) % 4, currentRound + 1, 1)
                    if curScore >= finalScore:  # 所有情况搞一个列表，选出分值最高的
                        finalScore = curScore
                        choice = d
        else:
            phase = 1
            if len(actions) > 5 or currentRound <= 0.4*self.maxRounds:  # 待调整
            # if len(actions) > 5:
                return actions[0]
            else:
                depth = 4
                for pos in actions:
                    newBoard = board.copy()
                    newBoard.add(self.isFirst, pos)
                    curScore = self._minMaxRecurNF(newBoard, depth, phase + 1, currentRound, 0)
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

