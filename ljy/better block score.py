# 基础版minmax 算法
# 创建于2020年5月8日 by Czarja
# 添加αβ剪枝，2020 5 09 by DXLi
# 动态深度


class Player:
    def __init__(self, isFirst, array):
        # 初始化
        self.isFirst = isFirst
        self.array = array
        self.maxValue = 2E9
        self.weight = [1, 2, 4, 8, 16, 32, 64, 128, 259, 519, 1039, 2079, 4159]
        self.marginWeight = [2E9, 8, 4, 0, 0, 0, 0]+[0]*25
        self.maxRounds = len(array)
        self.totalTime = 5.0
        self.threshold = self.maxRounds * 0.15  # 开启时间控制的阈值

    # 不会修改board，只是针对position情况返回所有可以下棋的位置列表
    @staticmethod
    def getActions(currentRound, board, peer):
        ownSidePos = board.getNext(peer, currentRound)
        otherSidePos = board.getNone(not peer)
        if len(ownSidePos) == 2:
            return ownSidePos, otherSidePos
            # otherSidePos.insert(0, ownSidePos)  # 己方位置插在对方位置之前，更适合alpha beta剪枝工作
        else:
            return None, otherSidePos

    def getDepth(self, currentRound, board):  # 动态调深度不太好，现在在搜索开始前把深度定死
        depth = 8
        if currentRound > self.threshold:  # 阈值待调整
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

    def weightSum(self, lst):  # 棋子和作为总分
        return sum(map(self.weight.__getitem__, lst))

    def score(self, board, currentRound):  # 最简单的局面估值函数
        # 目前完全是玄学估值
        myScoreLst = board.getScore(self.isFirst)
        total = self.marginWeight[len(board.getNone(not self.isFirst))] - self.marginWeight[len(board.getNone(self.isFirst))]
        if board.getNext(self.isFirst, currentRound) is None:
            total = -self.weight[myScoreLst[-1]]/3  # 无空可走的情况酌情扣分
        else:
            total = 0
        RivalScoreLst = board.getScore(not self.isFirst)
        total += self.weightSum(myScoreLst) - self.weightSum(RivalScoreLst)
        return total

    def scoreMove(self, board):
        myScoreLst = board.getScore(self.isFirst)
        RivalScoreLst = board.getScore(not self.isFirst)
        total = self.weightSum(myScoreLst) - self.weightSum(RivalScoreLst)
        # move的情况空格有额外两分
        total += (len(board.getNone(self.isFirst)) - len(board.getNone(not self.isFirst))) * 2
        return total

    def _minMaxRecur(self, board, depth, phase, currentRound, alpha=-(2E9), beta=+(2E9)):
        # 返回值为局面估值
        if depth <= 0 or currentRound >= self.maxRounds:
            if phase == 1 or phase == 2:
                return self.score(board, currentRound)
            else:  # 是move之后的下一步
                return self.scoreMove(board)
        peer = not bool(phase % 2)
        flag = bool(peer == self.isFirst)  # flag = True时为自己回合，False时为先手方回合
        if phase == 2 or phase == 3:
            if phase == 3:
                currentRound += 1
            for d in [0, 1, 2, 3]:
                newBoard = board.copy()
                if newBoard.move(peer, d):
                    curScore = self._minMaxRecur(newBoard, depth - 1, (phase + 1) % 4, currentRound, alpha, beta)
                    if not flag and (curScore < beta):
                        beta = curScore
                        if alpha >= beta:
                            return alpha
                    elif flag and (curScore > alpha):
                        alpha = curScore
                        if alpha >= beta:
                            return beta
        else:
            nextMove, posLst = Player.getActions(currentRound, board, peer)
            if nextMove is not None:
                posLst.insert(0, nextMove)  # 插在最前面，方便alphabeta剪枝
            if len(posLst) < 5:  # 可以下的空比较少时才搜索
                for pos in posLst:
                    newBoard = board.copy()
                    newBoard.add(peer, pos)
                    curScore = self._minMaxRecur(newBoard, depth-1, phase + 1, currentRound, alpha, beta)
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
                curScore = self._minMaxRecur(newBoard, depth-1, phase + 1, currentRound, alpha, beta)
                return curScore
        return alpha if flag else beta

    def minmaxDecisionF(self, board, currentRound, mode):  # 针对先手进攻局
        choice = None
        finalScore = -self.maxValue
        if mode[0] == '_':
            return None
        if mode == 'direction':
            # phase 0 1 2 3，分别先手落子、后手落子、先手移动、后手移动
            depth = self.getDepth(currentRound, board)
            for d in [0, 1, 2, 3]:
                newBoard = board.copy()
                if newBoard.move(self.isFirst, d):
                    curScore = self._minMaxRecur(newBoard, depth, 3, currentRound)
                    if curScore >= finalScore:  # 所有情况搞一个列表，选出分值最高的
                        finalScore = curScore
                        choice = d
        else:
            next_pos, actions = Player.getActions(currentRound, board, self.isFirst)
            if len(actions) > 5 and (next_pos is not None):
                return next_pos
            else:
                depth = self.getDepth(currentRound, board)
                if next_pos is not None:
                    actions.append(next_pos)
                for pos in actions:
                    newBoard = board.copy()
                    newBoard.add(self.isFirst, pos)
                    curScore = self._minMaxRecur(newBoard, depth, 1, currentRound)
                    if curScore >= finalScore:
                        finalScore = curScore
                        choice = pos
        return choice

    def minmaxDecisionNF(self, board, currentRound, mode):
        choice = None
        finalScore = -self.maxValue
        if mode[0] == '_':
            return None
        if mode == 'direction':
            # phase 0 1 2 3
            depth = self.getDepth(currentRound, board)
            for d in [0, 1, 2, 3]:
                newBoard = board.copy()
                if newBoard.move(self.isFirst, d):
                    curScore = self._minMaxRecur(newBoard, depth, 0, currentRound + 1)
                    if curScore >= finalScore:  # 所有情况搞一个列表，选出分值最高的
                        finalScore = curScore
                        choice = d
        else:
            next_pos, actions = Player.getActions(currentRound, board, self.isFirst)
            if len(actions) > 5 and (next_pos is not None):
                return next_pos
            else:
                depth = self.getDepth(currentRound, board)
                if next_pos is not None:
                    actions.append(next_pos)
                for pos in actions:
                    newBoard = board.copy()
                    newBoard.add(self.isFirst, pos)
                    curScore = self._minMaxRecur(newBoard, depth, 2, currentRound)
                    if curScore >= finalScore:
                        finalScore = curScore
                        choice = pos
        return choice

    def output(self, currentRound, board, mode):
        if self.isFirst:
            return self.minmaxDecisionF(board, currentRound, mode)
        else:
            return self.minmaxDecisionNF(board, currentRound, mode)
