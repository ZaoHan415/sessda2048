# sessda2048
 
## 使用

- 把技术组写的那个[sessdsa.2048](https://github.com/pkulab409/sessdsa.2048)整个拷到本地
- 修改variables.py里的路径
- 直接运行main.py

## 目前状态

- Random player拷自技术组
- Stupid player拷自玩家
- 基础的Minmax算法已经实现了。可能的改进方式：
  - [x] 加入alpha-beta剪枝(Done by [@D-X-Li](https://github.com/D-X-Li))
  - [ ] 调整估值函数，可以看[这个对局](http://162.105.17.143:9580/match/liGPdQ48Hg/)，其中12号小萝莉的估值函数为直接求和，13号为平方和。当大棋子权重调高后，更容易合成出高价值棋子，但13号的子儿反而更容易被吃掉了。
  - [ ] 采用numpy获得更快速的计算体验（？）
  - [ ] 如何针对大怂包这样的拖延时间策略优化？
  - [ ] 如何降低一开始棋子较少时对大量空位的搜索耗时？

### 20.5.8

- 增加了Minmax算法，Stable和Preview两个版本