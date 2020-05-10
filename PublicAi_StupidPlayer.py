import random

class ABNode:
    def __init__(self, board, currentRound, mode, isFirst, parent = None, type = True,
                 alpha = [-1000000, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                 beta = [1000000, 0, 0, 0, 0, 0, 0, 0, 0, 0]):
        '''
        初始化
        '''
        self.board = board  # 棋盘局面，为Chessboard类
        self.currentRound = currentRound    # 当前轮数，从0开始
        self.mode = mode  # 游戏进行状态：position或direction
        self.isFirst = isFirst  # 此节点执子方是否为先手方
        self.parent = parent    # 父节点
        self.children = {}  # 子节点的字典，以操作为key，子节点为value
        self.all_actions = []  # 当前局面下的可行操作
        # self.win = 0 # 以此节点为根的树中赢的次数
        self.situation = None   # 当前节点尚未落子的时候的局势好坏
        # 节点是否是Max节点，是则为True，否则为False，为Min节点
        # 有父节点则为父节点type的否，无父节点则直接定义
        if self.parent:
            self.type = not self.parent.type
        else:
            self.type = type
        self.alpha = alpha  # 此节点的alpha值，即根节点对应玩家的赢面最小值
        self.beta = beta    # 此节点的beta值，即根节点玩家对应的赢面最大值
        self.cut_factor = None  # 此节点的AB剪枝的节点的取值

    def expandAll(self):
        '''
        根据此时的 aall_actions生成所有可能的子节点
        对死棋进行特殊处理
        '''
        a_board = self.board.copy()

        # 死棋
        if self.all_actions == [None]:
            if self.mode == 'position':
                self.children[None] = ABNode(board=a_board,
                                             currentRound=self.currentRound,
                                             mode='position' if self.isFirst else 'direction',
                                             isFirst=not self.isFirst,
                                             parent=self,
                                             alpha=self.alpha,
                                             beta=self.beta)

            elif self.mode == 'direction':
                self.children[None] = ABNode(board=a_board,
                                             currentRound=self.currentRound if self.isFirst else (
                                                     self.currentRound + 1),
                                             mode='direction' if self.isFirst else 'position',
                                             isFirst=not self.isFirst,
                                             parent=self,
                                             alpha=self.alpha,
                                             beta=self.beta)
        # 没有死棋
        else:
            for action in self.all_actions:
                if action not in self.children.keys():
                    a_board = self.board.copy()
                    if self.mode == 'position':
                        a_board.add(self.isFirst, action)
                        self.children[action] = ABNode(board=a_board,
                                                       currentRound=self.currentRound,
                                                       mode='position' if self.isFirst else 'direction',
                                                       isFirst=not self.isFirst,
                                                       parent=self,
                                                       alpha=self.alpha,
                                                       beta=self.beta)

                    elif self.mode == 'direction':
                        a_board.move(self.isFirst, action)
                        self.children[action] = ABNode(board=a_board,
                                                       currentRound=self.currentRound if self.isFirst else (
                                                               self.currentRound + 1),
                                                       mode='direction' if self.isFirst else 'position',
                                                       isFirst=not self.isFirst,
                                                       parent=self,
                                                       alpha=self.alpha,
                                                       beta=self.beta)

    def expand(self):
        '''
        由当前节点扩展下一个需要探索的节点
        注意不是所有可能的节点全部拓展，而是只拓展一个
        '''

        # 选择哪个操作进行拓展就让神经网络决定，目前还没有写神经网络就等概率选择
        # 为了适应死棋继续的规则，如果all_actions为空，则直接生成完全一样的节点
        # 为了不生成已有节点，每生成一次就把对应操作从all_action中去掉
        action = self.all_actions.pop()

        a_board = self.board.copy()

        # 死棋
        if action == None:
            if self.mode == 'position':
                self.children[action] = ABNode(board=a_board,
                                                   currentRound=self.currentRound,
                                                   mode='position' if self.isFirst else 'direction',
                                                   isFirst=not self.isFirst,
                                                   parent=self,
                                                   alpha=self.alpha,
                                                   beta=self.beta)
            elif self.mode == 'direction':
                self.children[action] = ABNode(board=a_board,
                                                   currentRound=self.currentRound if self.isFirst else (
                                                               self.currentRound + 1),
                                                   mode='direction' if self.isFirst else 'position',
                                                   isFirst=not self.isFirst,
                                                   parent=self,
                                                   alpha=self.alpha,
                                                   beta=self.beta)

        # 没有死棋
        else:
            if self.mode == 'position':
                a_board.add(self.isFirst, action)
                self.children[action] = ABNode(board=a_board,
                                                   currentRound=self.currentRound,
                                                   mode='position' if self.isFirst else 'direction',
                                                   isFirst=not self.isFirst,
                                                   parent=self,
                                                   alpha=self.alpha,
                                                   beta=self.beta)
            elif self.mode == 'direction':
                a_board.move(self.isFirst, action)
                self.children[action] = ABNode(board=a_board,
                                                   currentRound=self.currentRound if self.isFirst else (self.currentRound + 1),
                                                   mode='direction' if self.isFirst else 'position',
                                                   isFirst=not self.isFirst,
                                                   parent=self,
                                                   alpha=self.alpha,
                                                   beta=self.beta)

        return self.children[action]

    def select(self):
        '''
        选择对于当前节点的执子方来说的最优节点
        '''
        # Max节点
        if self.type:
            max_situation = [-1000000, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            best_action = None
            for action in self.children.keys():
                if self.children[action].situation > max_situation:
                    max_situation = self.children[action].situation
                    best_action = action
            self.situation = max_situation
        # Min节点
        else:
            min_situation = [1000000, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            best_action = None
            for action in self.children.keys():
                if self.children[action].situation < min_situation:
                    min_situation = self.children[action].situation
                    best_action = action
            self.situation = min_situation

        return best_action, self.children[best_action]


    def grow(self, height = 0, max_height = 2):
        '''
        从当前节点开始AlphaBeta剪枝生长，返回决策操作
        '''
        if self.currentRound >= 500:
            self.parent.grow(height - 1)
        else:
            if height < max_height:
                if not self.children:
                    self.getAllActions()

                while self.all_actions:
                    if self.alpha < self.beta:
                        self.expand().grow(height + 1)
                    else:
                        self.all_actions = []

                if height == 0:
                    return self.select()[0]
                else:
                    self.select()

                if self.type:
                    self.parent.beta = min(self.alpha, self.parent.beta)
                else:
                    self.parent.alpha = max(self.beta, self.parent.alpha)

                self.parent.grow(height - 1)

            elif height == max_height:
                # self.getAllActions()
                # self.expandAll()
                #
                # for child in self.children.values():
                #     self.win -= child.judge()
                #
                # if self.type:
                #     self.parent.beta = min(self.win, self.parent.beta)
                # else:
                #     self.parent.alpha = max(self.win, self.parent.alpha)
                self.judge()

                if self.type:
                    self.parent.beta = min(self.situation, self.parent.beta)
                else:
                    self.parent.alpha = max(self.situation, self.parent.beta)


    def judge(self):
        '''
        判断当前局面的优势
        '''
        my_score = self.myScore()
        its_score = self.itsScore()

        my_score = [my_score.count(i) for i in range(10, 0, -1)]
        its_score = [its_score.count(i) for i in range(10, 0, -1)]

        if self.type:
            self.situation = [my_score[i] - its_score[i] for i in range(10)]
        else:
            self.situation = [its_score[i] - my_score[i] for i in range(10)]

        return self.situation

    def myScore(self):
        my_score = self.board.getScore(self.isFirst)
        my_score.sort(reverse=True)
        return my_score

    def itsScore(self):
        its_score = self.board.getScore(not self.isFirst)
        its_score.sort(reverse=True)
        return its_score


    def getAllActions(self):
        '''
        获取所有可能操作
        如果死棋了，则添加None
        '''
        if self.mode == "position":
            myPosition = self.board.getNext(self.isFirst, self.currentRound)
            positionList = [myPosition] if myPosition else []
            positionList.extend(self.board.getNone(not self.isFirst))
            random.shuffle(positionList)
            # 死棋异常处理
            self.all_actions = positionList if positionList else [None]
            return positionList
        elif self.mode == "direction":
            directionList = []
            for i in range(4):
                a_board = self.board.copy()
                if a_board.move(self.isFirst, i):
                    directionList.append(i)
            random.shuffle(directionList)
            # 死棋异常处理
            self.all_actions = directionList if directionList else [None]
            return directionList
        else:
            raise AssertionError(f"no such mode: {self.mode}")

class ABMCTS:
    def __init__(self, currentRound, board, mode, isFirst):
        '''
        初始化生成根节点
        '''
        self.root = ABNode(board=board,
                         currentRound=currentRound,
                         mode=mode,
                         isFirst=isFirst,
                         parent=None,
                         type=True)

    def output(self):
        return self.root.grow()

class Player:
    def __init__(self, isFirst, array):
        self.isFirst = isFirst
        self.array = array

    def output(self, currentRound, board, mode):
        # print(currentRound)
        MCTS = ABMCTS(currentRound, board, mode, self.isFirst)
        action = MCTS.output()
        return action