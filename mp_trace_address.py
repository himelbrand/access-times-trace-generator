import sys
import random
from functools import reduce
from calc_thresholds import calcThresholds
read_times = {
    # 'HDD1':{
    #     'name':'WD Black 6TB (2015)',
    #     'min':1.6,
    #     'avg':4.51,
    #     'max':6.96,
    #     'rl':4.167,
    #     'st':8.5
    # },
    'HDD1':{
        'name':'WD VelociRaptor 1TB',
        'min':1.23,
        'avg':1.64,
        'max':1.9,
        'rl':3.0,
        'st':6.9
    },
    'HDD2':{
        'name':'Seagate Barracuda 1TB',
        'min':0.6,
        'avg':0.81,
        'max':1,
        'rl':4.1,
        'st':12.7
    },
    'HDD3':{
        'name':'Hitachi Deskstar 7K1000 1TB',
        'min':0.4,
        'avg':0.71,
        'max':0.8,
        'rl':4.1,
        'st':13
    },
    # 'HDD2':{
    #     'name':'WD Blue 6TB (2015)',
    #     'min':0.6,
    #     'avg':0.91,
    #     'max':1.1,
    #     'rl':5.56
    # },
    # 'HDD3':{
    #     'name':'WD Red 10TB (2017)',
    #     'min':1.2,
    #     'avg':1.94,
    #     'max':2.6,
    #     'rl':5.56
    # },
    'SSD1':{
        'name':'WD Black SN750 NVMe PCIe M.2 500GB (2019)',
        'min':36.8,
        'avg':46.4,
        'max':52.6,
        'st':35
    },
    'SSD2':{
        'name':'WD Blue 500GB (2016)',
        'min':18.5,
        'avg':28.7,
        'max':38.9,
        'st':100
    }
}

if __name__ == "__main__":
    input_file = 'input/'+sys.argv[1]
    ths = calcThresholds()
    drives = sys.argv[3].split('#')
    block_sizes = [512,1024,4098,1048576]
    size_names = ['512b','4kb']#['512b','1kb','4kb','1mb']
    hps = ['0.225','1.1']#['0.225','0.35','1.1','250.1']
    if '-s' in sys.argv:
        seed = sys.argv[sys.argv.index('-s') + 1]
    else:
        seed = 27021991
    random.seed(seed)
    with open(input_file) as f:
        for ext_name,block_size,hp in zip(size_names,block_sizes,hps):
            f.seek(0)
            out_file = 'out_ths/hmp_2_%s_'%ext_name+sys.argv[1]
            with open(out_file,'w') as out:
                line = f.readline()
                while line:
                    if 'format=gradle' in sys.argv:
                        addresses = [int(line.split()[0],16)]
                    elif 'format=address' in sys.argv:
                        addresses = [int(line.split()[1],16)]
                    elif 'format=arc' in sys.argv:
                        addresses = range(int(line.split()[0]),int(line.split()[0])+int(line.split()[1]))
                    elif 'format=oltp' in sys.argv:
                        addresses = [int(line.split(',')[1])]
                    elif 'format=lirs' in sys.argv:
                        addresses = [int(line)]
                    else:
                        addresses = [int(line.split()[-1],16)]
                    if not addresses:
                        print('Error: missing format argument')
                        exit(1)
                    line = line.rstrip()
                    for address in addresses:
                        mpi = 0
                        while mpi < len(ths) and address > ths[mpi]:
                            mpi+=1
                        drive = drives[mpi]
                        min_read = read_times[drive]['min']
                        max_read = read_times[drive]['max']
                        avg_read = read_times[drive]['avg']
                        read_rate = random.triangular(min_read,max_read,avg_read)
                        mp = block_size/read_rate #gives miss penalty in microseconds
                        if 'HDD' in drive:
                            mp += read_times[drive]['rl']*1000 + read_times[drive]['st']*1000
                        else:
                            mp += read_times[drive]['st']
                        out.write(str(address)+' %s %.2f'%(hp,mp)+'\n')
                    line = f.readline()
    #TODO: add support for commpression 
    
    #gradle ths: 56767721354031354533962668594282754802#170318962904182302937531091057095545710#340281991432906288356376217369192469966
    #gradle mps: 150#20004#20044
    #gradle hp: 1.1
    #gradle entry size: 4KB
    #gradle partition: SSD=16.667% HDD_local=33.3333% HDD_remote=50%
    #gradle trace cmd: python3 mp_trace_address.py build-cache 56767721354031354533962668594282754802#170318962904182302937531091057095545710#340281991432906288356376217369192469966 150#20004#20044 1.1 format=gradle -o hmp_4kb_gradle.trace
    
    #gradle ths: 56767721354031354533962668594282754802#170318962904182302937531091057095545710#340281991432906288356376217369192469966
    #gradle mps: 37.5#20001#20011
    #gradle hp: 0.35
    #gradle entry size: 1KB
    #gradle partition: SSD=16.667% HDD_local=33.3333% HDD_remote=50%
    #gradle trace cmd: python3 mp_trace_address.py build-cache 56767721354031354533962668594282754802#170318962904182302937531091057095545710#340281991432906288356376217369192469966 37.5#20001#20011 0.35 format=gradle -o hmp_1kb_gradle.trace
    
    #gradle ths: 56767721354031354533962668594282754802#170318962904182302937531091057095545710#340281991432906288356376217369192469966
    #gradle mps: 18.75#20000.5#20005.5
    #gradle hp: 0.225
    #gradle entry size: 512B
    #gradle partition: SSD=16.667% HDD_local=33.3333% HDD_remote=50%
    #gradle trace cmd: python3 mp_trace_address.py build-cache 56767721354031354533962668594282754802#170318962904182302937531091057095545710#340281991432906288356376217369192469966 18.75#20000.5#20005.5 0.225 format=gradle -o hmp_512b_gradle.trace
    
    #gcc ths: 805686080#4294967295
    #gcc mps: 150#20004
    #gcc hp: 1.1
    #gcc entry size: 4KB
    #gcc partition: SSD=1/4 HDD=3/4
    #gcc trace cmd: python3 mp_trace_address.py gcc.trace 805686080#4294967295 150#20004 1.1 -o hmp_4kb_gcc.trace format=address 
    
    #gcc ths: 805686080#4294967295
    #gcc mps: 37.5#20001
    #gcc hp: 0.35
    #gcc entry size: 1KB
    #gcc partition: SSD=1/4 HDD=3/4
    #gcc trace cmd: python3 mp_trace_address.py gcc.trace 805686080#4294967295 37.5#20001 0.35 -o hmp_1kb_gcc.trace format=address 
    
    #ps8 ths: 1066230#8308682
    #ps8 mps: 18.75#20000.5
    #ps8 hp: 0.225
    #ps8 entry size: 512B
    #ps8 partition: SSD=1/4 HDD=3/4
    #ps8 trace cmd: python3 mp_trace_address.py P8.lis 1066230#8308682 18.75#20000.5 0.225 format=arc -o hmp_512b_P8.trace
    
    #ps12 ths: 1575016#10272280
    #ps12 mps: 18.75#20000.5
    #ps12 hp: 0.225
    #ps12 entry size: 512B
    #ps12 partition: SSD=1/4 HDD=3/4
    #ps12 trace cmd: python3 mp_trace_address.py P12.lis 1575016#10272280 18.75#20000.5 0.225 format=arc -o hmp_512b_P12.trace

    ### new format

    ###Gradle
    #python mp_trace_address.py build-cache 56767721354031354533962668594282754802#170318962904182302937531091057095545710#340281991432906288356376217369192469966 SSD1#HDD2#HDD3 format=gradle