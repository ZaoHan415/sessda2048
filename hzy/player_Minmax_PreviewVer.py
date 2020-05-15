# 基础版minmax 算法
# 创建于2020年5月8日 by Czarja
# 添加αβ剪枝，2020 5 09 by DXLi


class Player:
    def __init__(self, isFirst, array):
        # 初始化
        self.isFirst = isFirst
        self.array = array
        self.maxValue = 2E9

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

    @staticmethod
    def weightSum(lst):  # 平方和作为总分
        total = 0
        for a in lst:
            total += a*a
        return total

    def score(self, board):  # 最简单的局面估值函数
        # 目前完全是玄学估值
        myScoreLst = board.getScore(self.isFirst)
        RivalScoreLst = board.getScore(not self.isFirst)
        total = sum(myScoreLst) - Player.weightSum(RivalScoreLst)/2
        # 一个空位价值1.5分
        total += len(board.getNone(self.isFirst))*1.5
        # 无路可走的情况要避免
        if Player.cannotMove(self.isFirst, board):
            return -self.maxValue
        elif Player.cannotMove(not self.isFirst, board):
            return self.maxValue
        else:
            return total

    def _minMaxRecur(self, board, depth, phase, currentRound, inc, alpha=-(2E9), beta=+(2E9)):
        # 返回值为局面估值
        if depth <= 0:
            return self.score(board)
        peer = not bool(phase % 2)
        flag = bool(peer == self.isFirst)
        if phase == 2 or phase == 3:
            if phase == 3:
                currentRound += 1
            # if currentRound > 150:
            #     if inc < 4:
            #         depth += 1
            #         inc += 1
            for d in [0, 1, 2, 3]:
                newBoard = board.copy()
                if newBoard.move(peer, d):
                    curScore = self._minMaxRecur(newBoard, depth-1, (phase + 1) % 4, currentRound, inc, alpha, beta)
                    if not flag and (curScore < beta):
                        beta = curScore
                        if alpha >= beta:
                            return alpha
                    if flag and (curScore > alpha):
                        alpha = curScore
                        if alpha >= beta:
                            return beta
        else:
            posLst = Player.getActions(currentRound, board, 'position', peer)
            posLstLen = len(posLst)
            if posLstLen > 10:
                depth -= 1
            elif posLstLen < 4:
                if inc < 3:
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
                if flag and (curScore > alpha):
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
                depth = 0
            elif currentRound < 60:
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
            if len(actions) > 12:
                depth = 0
            elif len(actions) > 8:
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
