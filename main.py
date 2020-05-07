import variables
import analyser as gsm
import round_match as rm


player1 = r'./player_Random.py'
player2 = r'./player_Random.py'
# 大战10回合
a = rm.main([player1, player2])
# 调用技术组的复盘程序
gameScreen = gsm.GameScreen()