import variables
import round_match as rm
# import analyser as gsm
# import neattool as nt
import time


player1 = r'./src/player_Minmax_PreviewVer.py'
# player2 = r'./player_Random.py'
player2 = r'./src/thanos.py'
foldername = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime())
# 大战10回合，会自动调用技术组的复盘程序
a = rm.main([player1, player2], savepath=foldername, debug=True, REPEAT=10, MAXTIME=10)