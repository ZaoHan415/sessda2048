# 基础版minmax 算法
# 创建于2020年5月8日 by Czarja
# 添加αβ剪枝，2020 5 09 by DXLi
# 动态深度
import numpy


class Player:
    def __init__(self, isFirst, array):
        # 初始化
        self.isFirst = isFirst
        self.array = array
        self.maxValue = 2E9
        # self.weight = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096]
        # self.weight = [1, 2, 4, 8, 16, 32, 64, 128, 259, 519, 1039, 2079, 4159]
        self.weight = [1, 2, 4, 8, 16, 32, 64, 128, 259, 519, 1039, 2079, 4159]
        # self.weight = [2**i for i in range(13)]
        # self.weight = [1, 3, 7, 15, 31, 63, 127, 255, 511, 1023, 2047, 4095, 8191]
        self.maxRounds = len(array)
        self.totalTime = 5.0
        self.threshold = self.maxRounds * 0.15  # 开启时间控制的阈值

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

    def getDepth(self, currentRound, board):  # 动态调深度不太好，现在在搜索开始前把深度定死
        depth = 8
        if currentRound > self.threshold:  # 更新了，0.6待调整
            tLeft = board.getTime(self.isFirst)
            tEsti = (self.totalTime - tLeft) / float(currentRound)
            if tEsti > 0.0100:
                depth -= 2
            elif tEsti > 0.0095:
                depth -= 1
            elif tEsti < 0.005:
                depth += 6
            elif tEsti < 0.006:
                depth += 5
            elif tEsti < 0.007:
                depth += 4
            elif tEsti < 0.009:
                depth += 3
        return depth

    def weightSum(self, lst):  # 平方和作为总分
        return sum(map(self.weight.__getitem__, lst))

    def score(self, board, currentRound):  # 最简单的局面估值函数
        # 目前完全是玄学估值
        myScoreLst = board.getScore(self.isFirst)
        if board.getNext(self.isFirst, currentRound) is None:
            total = -self.weight[myScoreLst[-1]]/3  # 无空可走的负分是动态的
        else:
            total = 0
        RivalScoreLst = board.getScore(not self.isFirst)
        total += self.weightSum(myScoreLst) - self.weightSum(RivalScoreLst)
        # 一个空位价值1.5分
        # total += len(board.getNone(self.isFirst))*1.5
        # 无路可走的情况要避免
        # if Player.cannotMove(self.isFirst, board):
        #     return -self.maxValue
        # elif Player.cannotMove(not self.isFirst, board):
        #     return self.maxValue
        # else:
        return total

    def scoreMove(self, board, currentRound):
        myScoreLst = board.getScore(self.isFirst)
        RivalScoreLst = board.getScore(not self.isFirst)
        total = self.weightSum(myScoreLst) - self.weightSum(RivalScoreLst)
        total += (len(board.getNone(self.isFirst)) - len(board.getNone(not self.isFirst))) * 2
        return total

    def _minMaxRecur(self, board, depth, phase, currentRound, inc, alpha=-(2E9), beta=+(2E9)):
        # 返回值为局面估值
        if depth <= 0 or currentRound >= self.maxRounds:
            if phase == 1 or phase == 2:
                return self.score(board, currentRound)
            elif phase == 3 or phase == 0:
                return self.scoreMove(board, currentRound)
        peer = not bool(phase % 2)
        flag = bool(peer == self.isFirst)
        # flag = peer
        # flag = True时为自己回合，peer = True的时候为先手方回合
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
            if posLstLen < 5:
                # if inc < 4:
                #     depth += 1
                #     inc += 1
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
                newBoard.add(peer, posLst[0])
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
            depth = self.getDepth(currentRound, board)
            for d in actions:
                newBoard = board.copy()
                if newBoard.move(self.isFirst, d):
                    curScore = self._minMaxRecur(newBoard, depth, (phase+1) % 4, currentRound, 0)
                    if curScore >= finalScore:  # 所有情况搞一个列表，选出分值最高的
                        finalScore = curScore
                        choice = d
        else:
            phase = 0
            if len(actions) > 6 and board.getNext(self.isFirst, currentRound):  # 待调整
                return board.getNext(self.isFirst, currentRound)
            else:
                depth = self.getDepth(currentRound, board)
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
            depth = self.getDepth(currentRound, board)
            for d in actions:
                newBoard = board.copy()
                if newBoard.move(self.isFirst, d):
                    curScore = self._minMaxRecur(newBoard, depth, (phase + 1) % 4, currentRound + 1, 1)
                    if curScore >= finalScore:  # 所有情况搞一个列表，选出分值最高的
                        finalScore = curScore
                        choice = d
        else:
            phase = 1
            if len(actions) > 6 and board.getNext(self.isFirst, currentRound):  # 待调整
                return board.getNext(self.isFirst, currentRound)
            else:
                depth = self.getDepth(currentRound, board)
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