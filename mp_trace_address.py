import sys
if __name__ == "__main__":
    input_file = 'input/'+sys.argv[1]
    try:
        out_file = 'out_ths/hmp_'+sys.argv[1] if '-o' not in sys.argv else 'out_ths/'+sys.argv[sys.argv.index('-o')+1]
    except:
        print('Error: improper use of -o argument')
        exit(1)
    ths = [int(x) for x in sys.argv[2].split('#')]
    mps = sys.argv[3].split('#')
    hp = sys.argv[4]
    with open(input_file) as f:
        with open(out_file,'w') as out:
            line = f.readline()
            while line:
                if 'format=gradle' in sys.argv:
                    addresses = [int(line.split()[0],16)]
                elif 'format=address' in sys.argv:
                    addresses = [int(line.split()[1],16)]
                elif 'format=arc' in sys.argv:
                    addresses = [int(line.split()[0])]
                if not addresses:
                    print('Error: missing format argument')
                    exit(1)
                line = line.rstrip()
                for address in addresses:
                    mpi = 0
                    while mpi < len(ths) and address > ths[mpi]:
                        mpi+=1
                    mp = mps[mpi]
                    out.write(line+' '+hp+' '+mp+'\n')
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