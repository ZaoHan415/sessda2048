import variables
import analyser as gsm
import round_match as rm


player1 = r'./playerA.py'
player2 = r'./playerB.py'
a = rm.main([player1, player2])
gameScreen = gsm.GameScreen()