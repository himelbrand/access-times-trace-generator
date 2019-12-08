import sys
import random

flatten = lambda l: [item for sublist in l for item in sublist]
valid_modes = ['random','brandom','rr','fixed-rand','fixed-rr','fixed-brand']
valid_formats = ['wiki','lirs','address','arc','gradle']#TODO: add more support

def line_parser(f):
    if f in ['lirs','gradle']:
        return lambda x: x
    if f == 'address':
        return lambda x: x.split(' ')[1]
    if f == 'arc':
        return lambda x: x.split(' ')[0]  
    if f == 'wiki':
        CONTAINS_FILTER = ["?search=", "&search=", "User+talk", "User_talk","User:", "Talk:", "&diff=", "&action=rollback", "Special:Watchlist"]
        STARTS_WITH_FILTER = ["wiki/Special:Search", "w/query.php","wiki/Talk:", "wiki/Special:AutoLogin", "Special:UserLogin", "w/api.php", "error:"]
        def parse_url(x):
            url = x.split(' ')[2]
            for s in STARTS_WITH_FILTER:
                if url.startwith(s):
                    return None
            for s in CONTAINS_FILTER:
                if s in url:
                    return None
            return url      
        return parse_url
    
def mp_generator(m,p,b):
    if p == None:
        return None
    if m == 'random':
        return lambda _: random.choice(p)
    if m == 'rr':
        i = -1
        def next_p(_):
            nonlocal i
            i = (i+1)%len(p)
            return p[i]
        return next_p
    pen_d = {}
    if m == 'fixed-rand':
        def next_p(line):
            pen = pen_d.get(line)
            if pen == None:
                pen = random.choice(p)
                pen_d[line] = pen
            return pen
        return next_p
    if m == 'fixed-rr':
        i = -1
        def next_p(line):
            nonlocal i
            pen = pen_d.get(line)
            if pen == None:
                i = (i+1)%len(p)
                pen_d[line] = p[i]
                pen =  p[i]
            return pen
        return next_p
    if m == 'brandom':
        p = flatten([[pen]*b[i] for i,pen in enumerate(p)])
        return lambda _: random.choice(p)
    if m == 'fixed-brand':
        p = flatten([[pen]*b[i] for i,pen in enumerate(p)])
        def next_p(line):
            pen = pen_d.get(line)
            if pen == None:
                pen = random.choice(p)
                pen_d[line] = pen
            return pen
        return next_p
    raise Exception('invalid mode selected!')

def parse_args(argc):
    if argc < 1:
        raise Exception('Usage: mp_trace.py <trace_file_path> [optional args]')
    trace_path = sys.argv[1]
    new_trace_path = 'mp'+trace_path
    penalties = ['200\n','400\n','800\n','1600\n','3200\n']
    hit_penalty = None
    delimiter = ' '
    sizes = None
    rrs_flag = False
    mode = 'random'
    f = 'lirs'
    randbias = None
    randbias_sizes = None
    seed = 0
    try:
        sys.argv.index('-rrs')
        rrs_flag = True
        try:
            i = sys.argv.index('-sizes') + 1
            if argc < i:
                raise Exception('Usage of size: -sizes N1#N2#N3#N4#..,#Nk , Ni is a integer representing a size in bytes')
            sizes = sys.argv[i].split('#')
            if len(sizes) < 1 or min([int(s) for s in sizes]) < 1:
                raise Exception('Usage of size: must contain et least one file size value, which is a positive integer')
            i = sys.argv.index('-crr') + 1
            if argc < i:
                raise Exception('Usage of crr: -crr <cache read rate>')
            hit_penalty = sys.argv[i]
            if int(hit_penalty) < 1:
                raise Exception('Usage of crr: -crr <cache read rate>, <cache read rate> must be a positive integer, representing the read rate of the cache in bytes/ms')
            i = sys.argv.index('-mrr') + 1
            if argc < i:
                raise Exception('Usage of mrr: -mrr N1#N2#N3#N4#..,#Nk , Ni is a integer representing a miss read rate in bytes/ms')
            penalties = [p+'\n' for p in sys.argv[i].split('#')] 
            if len(penalties) < 1 or min([int(p) for p in penalties]) < 1:
                raise Exception('Usage of mrr: must contain et least one miss read rate value, which is a positive integer')
            if max([int(p) for p in penalties]) > int(hit_penalty):
                raise Exception('chache read rate must be higher than the maximum miss read rate')
        except ValueError:
            raise Exception('when using -rrs you must also correctly use -size, -crr and -mrr')
        new_trace_path = 'rrs'+new_trace_path[2:]
    except ValueError:
        pass
    if not rrs_flag:
        try:
            i = sys.argv.index('-p') + 1
            if argc < i:
                raise Exception('Usage of penalties: -p N1#N2#N3#N4#..,#Nk , Ni is a integer representing a miss penalty')
            penalties = [p+'\n' for p in sys.argv[i].split('#')] 
            if len(penalties) < 1:
                raise Exception('Usage of penalties: must contain et least one miss penalty value')
        except ValueError:
            pass
        try:
            i = sys.argv.index('-hp') + 1
            if argc < i:
                raise Exception('Usage of hit penalty: -hp <hit-penalty> , <hit-penalty> is a integer representing the hit penalty')
            hit_penalty = sys.argv[i]
            if min([int(p) for p in penalties]) < int(hit_penalty):
                raise Exception('the lowest miss penalty shouldn\'t be lower than hit-penalty={}'.format(hit_penalty))
            new_trace_path = 'h'+new_trace_path
        except ValueError:
            pass
    try:
        i = sys.argv.index('-s') + 1
        if argc < i:
            raise Exception('Usage of seed: -s <seed> , <seed> is a integer')
        try:
            seed = int(sys.argv[i])
        except ValueError:
            raise Exception('Usage of seed: -s <seed> , <seed> is a integer')
        if len(penalties) < 1:
            raise Exception('Usage of penalties: must contain et least one miss penalty value')
    except ValueError:
        pass
    try:
        i = sys.argv.index('-d') + 1
        if argc < i:
            raise Exception('Usage of delimiter: -d " " (delimitier here is " " you can use any string with double quotes)')
        delimiter = sys.argv[i]
    except ValueError:
        pass
    try:
        i = sys.argv.index('-f') + 1
        if argc < i:
            raise Exception('Usage of format: -f <format> (<format> must be one of [wiki,lirs,address,arc,gradle], default is lirs)')
        f = sys.argv[i]
        if not(f in valid_formats):
            raise Exception('Usage of format: -f <format> (<format> must be one of [wiki,lirs,address,arc,gradle], default is lirs)')            
    except ValueError:
        pass
    try:
        i = sys.argv.index('-m') + 1
        if argc < i:
            raise Exception('Usage of mp mode: -m <mode> , <mode> is one of: [random,rr,fixed-rr,fixed-rand,brandom]')
        mode = sys.argv[i]
        if not (mode in valid_modes):
            raise Exception('Usage of mp mode: -m <mode> , <mode> is one of: [random,rr,fixed-rr,fixed-rand,brandom]')
        if  mode in ['brandom','fixed-brand'] and argc < i+1:
            raise Exception('Usage of mp mode - brandom(or fixed-brand): -m brandom <bias> , <bias> is of the form B1#B2#...#Bk where k is the number of penalties and Bi is an integer')
        if  mode in ['brandom','fixed-brand'] and argc < i+2 and rrs_flag:
            raise Exception('Usage of mp mode - brandom(or fixed-brand) when using -rrs: -m brandom <bias> <size-bias> , <bias> and <size-bias> are of the form B1#B2#...#Bk and BS1#BS2#...#BSm where k is the number of penalties and m is the number of sizes, Bi and BSi are integers')
        if mode in ['brandom','fixed-brand']:
            randbias =  [int(p) for p in sys.argv[i+1].split('#')]
            if rrs_flag:
                randbias_sizes = [int(p) for p in sys.argv[i+2].split('#')]
                if len(randbias_sizes) != len(sizes):
                    raise Exception('Usage of mp mode - brandom(or fixed-brand) when using -rrs: -m brandom <bias> <size-bias> , <bias> and <size-bias> are of the form B1#B2#...#Bk and BS1#BS2#...#BSm where k is the number of penalties and m is the number of sizes, Bi and BSi are integers')
            if len(randbias) != len(penalties):
                raise Exception('Usage of mp mode - brandom: -m brandom <bias> , <bias> is of the form B1#B2#...#Bk where k is the number of penalties and Bi is an integer')            
    except ValueError:
        pass    
    return trace_path,new_trace_path,penalties,delimiter,mode,randbias,f,seed,hit_penalty,sizes,randbias_sizes

if __name__ == "__main__":
    trace_path,new_trace_path,penalties,delimiter,mode,randbias,f,seed,hp,sizes,randbias_sizes = parse_args(len(sys.argv) - 1)
    random.seed(seed)
    og_trace = open(trace_path)
    new_trace = open(new_trace_path,'w')
    get_mp = mp_generator(mode,penalties,randbias)
    get_size = mp_generator(mode,sizes,randbias_sizes)
    get_key = line_parser(f)
    line = og_trace.readline()
    hp_text = '' if hp is None else delimiter+hp
    while line:
        mp = get_mp(get_key(line))
        line = line.rstrip()
        if get_size:
            size = get_size(get_key(line))
            new_trace.write(line+delimiter+size+delimiter+hp_text+delimiter+mp)
        else:
            new_trace.write(line+hp_text+delimiter+mp)
        line = og_trace.readline()
    og_trace.close()
    new_trace.close()
    #TODO: add support for commpression 