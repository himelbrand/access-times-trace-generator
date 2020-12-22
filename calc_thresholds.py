import sys
import math
from collections import Counter
def calcThresholds(flag=False):
    trace = 'input/' + sys.argv[1]
    portions = [int(p) for p in sys.argv[2].split('#')]
    s = sum(portions)
    fracs = [p/s for p in portions]
    fracs = [x+(sum(fracs[:i]) if i > 0 else 0) for i,x in zip(range(len(fracs)),fracs)]
    print(fracs)
    addresses = set()
    with open(trace) as f:
        line = f.readline()
        while line:
            if 'format=gradle' in sys.argv:
                address = [int(line.split()[0],16)]
            elif 'format=address' in sys.argv:
                address = [int(line.split()[1],16)]
            elif 'format=arc' in sys.argv:
                address = range(int(line.split()[0]),int(line.split()[0])+int(line.split()[1]))
            elif 'format=oltp' in sys.argv:
                address = [int(line.split(',')[1])]
            elif 'format=lirs' in sys.argv:
                address = [int(line)]
            else:
                address = [int(line.split()[-1],16)]
            for a in address:
                addresses.add(a)
            line = f.readline()
    addresses = list(addresses)
    addresses.sort()
    ths = [addresses[int(len(addresses)*f) if f<1.0 else -1] for f in fracs]
    count = Counter()
    for a in addresses:
        for t in ths:
            if a <= t:
                count[str(t)] += 1
                break
    if flag:
        print('#'.join([str(t) for t in ths]))
        print(len(addresses))
        print(count)
    else:
        return ths

if __name__ == '__main__':
    calcThresholds(flag=True)
    