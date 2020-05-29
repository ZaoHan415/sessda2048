import variables
import round_match as rm
import os
import shutil
import winrate_test
import copy
import re
import time


player1 = r'./winrate_test.py'


player2 = r'./player_Minmax_AlphaBeta_PreviewVer.py'

path='/Users/liujinyudemacbook/Documents/GitHub/sessda2048/'




def winrate(Q):
    winrate_test.P=Q+[0 for i in range(23)]
    a = rm.main([player1, player2],savepath=path+'_', debug=True, REPEAT=1, MAXTIME=5)
    f=open(path+'_/_.txt', mode='r')
    n=0
    i=0
    for line in f:
        a=re.search('win: [0-9]+ at',line)
        if a!=None:
            b=a.group()
            c=b.split()
            n+=int(c[1])
            
            i+=1
        if i==2:
            break
    f.close()
    shutil.rmtree(path+'_')
    return n
        
        
def search(win,lst):
    a=win
    R=lst
    for i in range(len(lst)):
        lst[i]+=2**(5-i)
        print(lst)
        b=winrate(lst)
        print(b)
        if b>a:
            a=b
            R=copy.copy(lst)
        lst[i]-=2**(6-i)
        print(lst)
        b=winrate(lst)
        print(b)
        if b>a:
            a=b
            R=copy.copy(lst)
        lst[i]+=2**(5-i)
    print(a,'iter')
    if a==win:
        return a,R
    else:
        return search(a,R)

Q=[2**(9-i) for i in range(9)]    

print(search(0,Q))
