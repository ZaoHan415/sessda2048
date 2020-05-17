# 基础版minmax 算法
# 创建于2020年5月8日 by Czarja
# 添加αβ剪枝，2020 5 09 by DXLi


class Player:
    def __init__(self, isFirst, array):
        # 初始化
        self.isFirst = isFirst
        self.array = array
        self.maxValue = 2E9
        self.weight = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096]

    @staticmethod
    def cannotMove(belong, board):  # 如果某方无路可走返回True
        for direction in [0, 1, 2, 3]:
            if board.move(belong, direction):
                return False
        return True

    @staticmethod
    def takeSecond(elem):
        return elem[1]

    def choosePos(self, board, posLst, peer, maximumAction):
        boardLst = []
        if len(posLst) <= maximumAction:
            for pos in posLst:
                newBoard = board.copy()
                newBoard.add(peer, pos)
                boardLst.append((pos, newBoard))
        else:
            tempLst = []
            for pos in posLst:
                newBoard = board.copy()
                newBoard.add(peer, pos)
                tempLst.append(((pos, newBoard), self.score(newBoard)))
            tempLst.sort(key=Player.takeSecond)
            if self.isFirst == peer:
                for x in tempLst[-maximumAction:]:
                    boardLst.append(x[0])
            else:
                for x in tempLst[0:maximumAction]:
                    boardLst.append(x[0])
        return boardLst

    def chooseDirection(self, board, peer, maximumAction):
        boardLst = []
        if maximumAction >= 4:
            for d in [0, 1, 2, 3]:
                newBoard = board.copy()
                if newBoard.move(peer, d):
                    boardLst.append((d, newBoard))
        else:
            tempLst = []
            for d in [0, 1, 2, 3]:
                newBoard = board.copy()
                if newBoard.move(peer, d):
                    tempLst.append(((d, newBoard), self.score(newBoard)))
            tempLst.sort(key=Player.takeSecond)
            if self.isFirst == peer:
                for x in tempLst[-maximumAction:]:
                    boardLst.append(x[0])
            else:
                for x in tempLst[0:maximumAction]:
                    boardLst.append(x[0])
        return boardLst

    # 不会修改board，只是针对position情况返回所有可以下棋的位置列表
    def getActions(self, currentRound, board, mode, peer, maximumAction=100):
        if mode == 'position':
            ownSidePos = board.getNext(peer, currentRound)
            otherSidePos = board.getNone(not peer)
            if len(ownSidePos) == 2:
                otherSidePos.append(ownSidePos)
            return self.choosePos(board, otherSidePos, peer, maximumAction)
        else:
            return self.chooseDirection(board, peer, 4)

    def weightSum(self, lst):  # 平方和作为总分
        total = 0
        for a in lst:
            total += self.weight[a]
        return total

    def score(self, board):  # 最简单的局面估值函数
        # 目前完全是玄学估值
        myScoreLst = board.getScore(self.isFirst)
        RivalScoreLst = board.getScore(not self.isFirst)
        total = self.weightSum(myScoreLst) - self.weightSum(RivalScoreLst)/2
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
            actions = self.getActions(currentRound, board, 'direction', peer)
            if phase == 3:
                currentRound += 1
            # if currentRound > 150:
            #     if inc < 4:
            #         depth += 1
            #         inc += 1
            for d in actions:
                curScore = self._minMaxRecur(d[1], depth-1, (phase + 1) % 4, currentRound, inc, alpha, beta)
                if not flag and (curScore < beta):
                    beta = curScore
                    if alpha >= beta:
                        return alpha
                if flag and (curScore > alpha):
                    alpha = curScore
                    if alpha >= beta:
                        return beta
        else:
            maximumAct = 3
            # if currentRound < 20:
            #     maximumAct = 5
            # elif currentRound < 60:
            #     maximumAct = 4
            posLst = self.getActions(currentRound, board, 'position', peer, maximumAction=maximumAct)
            # posLstLen = len(posLst)
            # if posLstLen < 4:
            #     if inc < 3:
            #         depth += 1
            #         inc += 1
            for pos in posLst:
                curScore = self._minMaxRecur(pos[1], depth-1, phase + 1, currentRound, inc, alpha, beta)
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
        choice = None
        finalScore = -self.maxValue
        depth = 2
        if mode[0] == '_':
            return None
        maximumAct = 3
        # if currentRound < 20:
        #     maximumAct = 5
        # elif currentRound < 60:
        #     maximumAct = 4
        actions = self.getActions(currentRound, board, mode, self.isFirst, maximumAction=maximumAct)
        if mode == 'direction':
            # phase 0 1 2 3
            phase = 2 if self.isFirst else 3
            if not self.isFirst:
                currentRound += 1
            # if currentRound < 100:
            #     depth = 1
            for d in actions:
                curScore = self._minMaxRecur(d[1], depth, (phase+1) % 4, currentRound, 0)
                if curScore >= finalScore:  # 所有情况搞一个列表，选出分值最高的
                    finalScore = curScore
                    choice = d[0]
        else:
            phase = 0 if self.isFirst else 1
            # if len(actions) > 12:
            #     depth = 0
            # elif len(actions) > 8:
            #     depth = 1
            for pos in actions:
                curScore = self._minMaxRecur(pos[1], depth, phase+1, currentRound, 0)
                if curScore >= finalScore:
                    finalScore = curScore
                    choice = pos[0]
        # print('stable', finalScore)
        return choice

    def output(self, currentRound, board, mode):
        return self.minMaxDecision(board, currentRound, mode)
