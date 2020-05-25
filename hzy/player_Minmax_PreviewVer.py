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
        # 各种奇怪的权重函数
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
                otherSidePos.append(ownSidePos)
            return otherSidePos
        else:
            return [0, 1, 2, 3]

    # 预测自己会不会比对方先超时，目前还不太好用
    def gonnaOutOfTime(self, currentRound, board):
        tLeftMe = board.getTime(self.isFirst)
        tLeftRival = board.getTime(not self.isFirst)
        if tLeftMe < tLeftRival:
            return (self.totalTime - tLeftMe) * self.maxRounds / currentRound > self.totalTime
        return False

    def weightSum(self, lst):  # 求和作为总分
        # 换成这种列表推导式后速度快了三倍
        return sum(map(self.weight.__getitem__, lst))

    def score(self, board):  # 最简单的局面估值函数
        # 目前完全是玄学估值
        myScoreLst = board.getScore(self.isFirst)
        RivalScoreLst = board.getScore(not self.isFirst)
        total = self.weightSum(myScoreLst) - self.weightSum(RivalScoreLst)/2
        # 一个空位价值1.5分
        total += len(board.getNone(self.isFirst))*1.5
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
        if phase == 2 or phase == 3:
            if phase == 3:
                currentRound += 1
            for d in [0, 1, 2, 3]:
                newBoard = board.copy()
                if newBoard.move(peer, d):
                    curScore = self._minMaxRecur(newBoard, depth-1, (phase + 1) % 4, currentRound, inc, alpha, beta)
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
            if currentRound > 100:
                if self.gonnaOutOfTime(currentRound, board):
                    # 如果快超时了就少搜一层
                    depth -= 1
                elif inc < 4:
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
        return alpha if flag else beta

    def minMaxDecision(self, board, currentRound, mode):  # 返回值为要进行的操作
        actions = Player.getActions(currentRound, board, mode, self.isFirst)
        choice = None
        finalScore = -self.maxValue
        depth = 2
        if mode[0] == '_':
            return None
        if mode == 'direction':
            # phase 0 1 2 3
            phase = 2 if self.isFirst else 3
            if not self.isFirst:
                currentRound += 1
            if currentRound < 10:
                depth = 1
            for d in actions:
                newBoard = board.copy()
                if newBoard.move(self.isFirst, d):
                    curScore = self._minMaxRecur(newBoard, depth, (phase+1) % 4, currentRound, 0)
                    if curScore >= finalScore:  # 所有情况搞一个列表，选出分值最高的
                        finalScore = curScore
                        choice = d
        else:
            phase = 0 if self.isFirst else 1
            if len(actions) > 14:
                depth = 1
            for pos in actions:
                newBoard = board.copy()
                newBoard.add(self.isFirst, pos)
                curScore = self._minMaxRecur(newBoard, depth, phase+1, currentRound, 0)
                if curScore >= finalScore:
                    finalScore = curScore
                    choice = pos
        return choice

    def output(self, currentRound, board, mode):
        return self.minMaxDecision(board, currentRound, mode)


# if __name__ == '__main__':
#     a = Player(True, [])
#     print(a.weightSum([1, 4]))