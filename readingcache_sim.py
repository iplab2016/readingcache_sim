'''
Script Name	: readingcache_sim.py
Author	        : Haifeng Li
Created	        : 16th May 2016
Last Modified	: 16th May 2016
Version		: 0.1

Modifications	: 

Description     :This script will simulate the data transfering process
                 in the two-layer high-speed caching system for CCN
                 to verify minimum reading cache size.
'''

import time
import sys
import os


#data packet size (bytes)
PACKET_SIZE = 1500
#the number of data packets in one chunk
CHUNK_PACKET_NUM = 8

#new row access time of dram (second)
NEW_TIME = 30.0*(10**(-9))
#old row access time of dram (second)
OLD_TIME = 0.625*(10**(-9))

#the lifetime of one chunk cached in reading cache
rho = 0  

#user experienced data rate (bps)
Vu = 1024**3

def color_print(color, mes):
    if color == 'r':
        fore = 31
    elif color == 'g':
        fore = 32
    elif color == 'b':
        fore = 36
    elif color == 'y':
        fore = 33
    else:
        fore = 37
    color = "\x1B[%d;%dm" % (1,fore)
    print "%s %s\x1B[0m" % (color,mes)

def usage(no):
    print " Usage: %s [packets_num]" % sys.argv[0]
    print " packets_num is the number of data packets in one chunk"
    print " \tThe default value of packets_num is 8."
    sys.exit(no)

if len(sys.argv) > 2:
    color_print('r', 
          "Error: The number of parameters is  out of range")
    usage(2)
else:
     try:
         packets_num = int(sys.argv[1])
     except:
         color_print('r', "Error: packets_num have to be digit(float/int)")
         usage(3)

#The number in a row in dram
if not locals().has_key('packets_num'):
    packets_num = CHUNK_PACKET_NUM

#chunk size(bytes)
chunk_size = packets_num*PACKET_SIZE

#The lifetime of one chunk cached in reading cache
rho = float(chunk_size)/Vu

#The theoretical throughput of the caching system (Gbps)
#Vd = float(8*chunk_size)/(60+(0.625*chunk_size/8))
#Vd = Vd*(1024**3)

#Let remaining_chunks be the number of remaining chunks in reading cache
#The value in remaining_chunks stands for the number of the remaining chunks\ 
#                        which have the same number of remaining data packets
#The index plus 1 stands for the remaining data packets in these chunks
#For example, remaining_chunks[0] = 100, 
#that means there are 100 chunks which only have 1 data packets in reading cache
remaining_chunks = [0]*packets_num


#reading cache, 
#for a rho time, the number of chunks transfered from dram to reading cache
chunks_num = int(rho/((NEW_TIME-OLD_TIME)+(chunk_size/8)*OLD_TIME))
print "For rho time, the number of chunks trasfered by dram:%d" % chunks_num
print "The maximum throughput of the dram: %.2f Gbps" % (
 (chunk_size/((NEW_TIME-OLD_TIME)+(chunk_size/8)*OLD_TIME))*8/1024/1024/1024)

#pre-set the size of reading cache as rc_size (the number of data packets)
rc_size = (8.0*chunk_size*chunk_size*(1024**3))/(60*Vu+(0.625*chunk_size*Vu/8))
rc_size = int(rc_size/1500)

last_index = packets_num - 1
old_size = 0
while True:
    #total response,
    #the number of data packets sent from reading cache
    total_res = 0

    #The number of data packets cached in reading cache
    sram_used = 0

    ##fetch data packets in batch from dram to sram
    if sum(remaining_chunks) == 0:
        remaining_chunks[packets_num-1] =  chunks_num
    else:
        #reading cache responses the requested data packets
        for i in range(packets_num): 
            print "remaining_chunks[%d]=%d"  % (i, remaining_chunks[i])
            #number of responses which will be sent by sram
            total_res = total_res + remaining_chunks[i]
       
        print "The realtime throughput of the caching system = %.2f Gbps" %(
                                  total_res*PACKET_SIZE*8/rho/1024/1024/1024)

        #re-calculate remaining cell
        for i in range(packets_num-1):
            remaining_chunks[i] = remaining_chunks[i+1]
            sram_used = sram_used + remaining_chunks[i]*(i+1) 
         
        #After reading cache deletes the data packets 
        #   which have been requested for one time.
        #Let fetching_chunks be the number of chunks 
        #   which can be transfered from dram to sram.
        fetching_chunks = total_res/packets_num

        #Fetch data packets in batch from dram to reading cache
        if (sram_used + chunks_num*packets_num) > rc_size:
            if (sram_used + fetching_chunks*packets_num) < rc_size:
                remaining_chunks[packets_num-1] = fetching_chunks
                print "Fetch %d chunks in batch 1" %(
                                     remaining_chunks[packets_num-1])
            else:
                fetching_chunks = (rc_size - sram_used)/packets_num
                remaining_chunks[packets_num-1] = fetching_chunks
                print "Fetch %d chunks in batch 2" %(
                                     remaining_chunks[packets_num-1])

        elif (sram_used + chunks_num*packets_num) <= rc_size:
            print "Fetch %d chunks in batch 3" % chunks_num
            remaining_chunks[packets_num-1] = chunks_num

        sram_used = 0
        total_res = 0
        for i in range(packets_num):
           total_res = total_res + remaining_chunks[i]
           sram_used = sram_used + remaining_chunks[i]*(i+1)
        print "The pre-set reading cache size = %.2f Mb" %(
                                  rc_size*8*1500.0/1024/1024)
        print "\tThe number of data packets = %d" % (rc_size)
        print "The actually used size of reading cache = %.2f Mb" %(
                                          sram_used*8*1500.0/1024/1024)
        print "\tThe number of data packets = %d " % (sram_used)
        
        if old_size == sram_used:
            print "The optimized size of reading cachet = %.2f Mb" %(
                                          sram_used*8*1500.0/1024/1024)
            print "\tThe number of data packets = %d " % (sram_used)
            sys.exit(0)
        old_size = sram_used
    time.sleep(1) 

