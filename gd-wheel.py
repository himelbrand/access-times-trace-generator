import numpy as np 
import mmh3
from datetime import timedelta
import time
import os.path
from os import path
# import sys
# import seaborn as sns
# import matplotlib.pyplot as plt 
def createTrace(ranges,p,m,num,hp=1):
    indecies = np.random.choice(range(len(ranges)),size=m,p=p)
    s = [np.random.randint(*ranges[i]) for i in indecies]
    ids = np.random.zipf(1.1,m)
    with open('GDW-workload%d.trace'%num,'w') as f:
        for i in range(m):
            f.write('%d %d %d\n'%(ids[i],hp,s[i]))
    print('GDW-workload%d'%num)
    # print(min(ids),max(ids),len(set(ids)))
    # plt.hist(ids)
    # plt.show()
    # input("llllll")
def parseWikiLine(x):
    CONTAINS_FILTER = ["?search=", "&search=", "User+talk", "User_talk","User:", "Talk:", "&diff=", "&action=rollback", "Special:Watchlist"]
    STARTS_WITH_FILTER = ["wiki/Special:Search", "w/query.php","wiki/Talk:", "wiki/Special:AutoLogin", "Special:UserLogin", "w/api.php", "error:"]
    url = x.split(' ')[2]
    for s in STARTS_WITH_FILTER:
        if url.startswith(s):
            return None
        for s in CONTAINS_FILTER:
            if s in url:
                return None
    return url      
def filterWiki(fname):
    if path.exists('clean_%s'%fname):
        return
    with open(fname, encoding='utf-8',errors='replace') as wiki:
        with open('clean_%s'%fname,'w') as f:
            line = wiki.readline()
            count = 1
            while line:
                url = parseWikiLine(line)
                if url != None:
                    key = str(int.from_bytes(mmh3.hash_bytes(url)[-8:],'big'))
                    f.write('%s\n'%key)
                line = wiki.readline()
                count += 1

def createWIKITrace(fname,ranges,p,num,hp=1,prec99=False,prec99_factor=10):
    with open(fname) as wiki:
        keys = wiki.readlines()
        m = len(keys)
        indecies = np.random.choice(range(len(ranges)),size=m,p=p)
        dic = dict()
        # s = [np.random.randint(*ranges[i]) for i in indecies]
        # ids = np.random.zipf(1.1,m)
        with open('out_wiki/%s_penalties%d%s.trace'%(fname,num,'_with99prec' if prec99 else ''),'w') as f:
            for i in range(m):
                key = keys[i].strip('\n ')
                if dic.get(key):
                    rng = dic.get(key)
                else:
                    rng = ranges[indecies[i]]
                    dic[key] = rng
                if np.random.rand() >= 0.99 and prec99:
                    mp = np.random.randint(*rng)*prec99_factor
                else:
                    mp = np.random.randint(*rng)
                f.write('%s %d %d\n'%(key,hp,mp))
    # print(min(ids),max(ids),len(set(ids)))
    # plt.hist(ids)
    # plt.show()
    # input("llllll")
def printTiming(t0):
    t = (time.time()-t0)
    print('time took: {}'.format(timedelta(seconds=t)))
if __name__ == '__main__':
    biases = [[0.8,0.15,0.05],[0.2,0.75,0.05],[0.5,0.25,0.25],[1.0]]
    ranges = [[(10,31),(120,181),(350,451)],[(10,31),(120,181),(350,451)],[(10,31),(120,181),(350,451)],[(20,401)]]
    for wikifile in ['wiki1190153705','wiki1190207720','wiki1190222124','wiki1190322952']:
        t0 = time.time()
        print('start filtering: %s'%wikifile)
        filterWiki(wikifile)
        printTiming(t0)
        print('done filtering: %s'%wikifile)
        for i in range(len(ranges)):
            t0 = time.time()
            createWIKITrace('clean_%s'%wikifile,ranges[i],biases[i],i+1)
            createWIKITrace('clean_%s'%wikifile,ranges[i],biases[i],i+1,prec99=True)
            print('done creating penalties trace number %d for %s'%(i+1,wikifile))
            printTiming(t0)