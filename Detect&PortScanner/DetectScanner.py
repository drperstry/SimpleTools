from scapy.all import *
import time
from functools import partial
import threading

def Analyze(pkt_dict,if_ip, pkt):
    # i get the IP and port from the packet
    ip=pkt['IP'].src
    port=None
    # if the packet is tcp or udp i can get the port
    if('TCP' in pkt):
        port=pkt['TCP'].dport
    elif('UDP' in pkt):
        port=pkt['UDP'].dport
    #if the packet destination is my network interface and (udp or tcp 'having port number')
    if(pkt['IP'].dst== if_ip and port):
        if(ip in pkt_dict):
            if(time.time()-5 <= pkt_dict[ip]['timer']):
                #assuming the scanning will be in ascending order
                if(port-1 == int(pkt_dict[ip]['prevPort'])):
                    pkt_dict[ip]['prevPort']=port
                    pkt_dict[ip]['counter']+=1
                    #here dont update time
                    pkt_dict[ip]['timer']=time.time()
                    if(pkt_dict[ip]['counter']>=15):
                        print(f'scan detected. The scanner originated from host {ip}')
                        #then delete the ip from the dict
                        del pkt_dict[ip]
                else:
                    #assuming there will not be a behavior where scanner scans random ports then scan 15 consecutive ports.
                    #set the record's counter=1 and timer=now and port to this port
                    pkt_dict[ip]={
                        'prevPort': port,
                        'timer': time.time(),
                        'counter': 1
                    }
            else:
                #set the record's counter=1 and timer=now and port to this port, since the time passed
                pkt_dict[ip]={
                    'prevPort': port,
                    'timer': time.time(),
                    'counter': 1
                }
        else:
            #add the ip to my dict
            pkt_dict[ip]={
                #prevePort -2 initially so it's not considered an actul port... 
                'prevPort': -2,
                'timer': time.time(),
                'counter': 1
            }
    else:
        #do nothing
        pass

def Sniffing(dev):
    # the sniff method will sniff the network interface and when a pakcet arrive it will deal wilth it alone.
    # the prn is telling the sniff method whenever a packet arrive, throw it into the method Analyze
    # and the newtork interface device and passing an empty dict to use it for the logic in Analyze method. 
    packets_dict={}
    #making sure it's a network interface (having an ip)
    try:
        ip=get_if_addr(dev)
    except:
        exit()
    # print(f'sniffing device with IP: {ip} now!')
    sniff(filter="ip", iface=dev, prn=partial(Analyze,packets_dict, ip))

#by running this, the detection will run forever!
def PSDetect():

    # getting all working interfaces!
    devs=scapy.all.get_working_ifaces()
    # creating threads
    
    threads=[]
    # threads sniffs for each interface
    for dev in devs:
        threads.append(threading.Thread(target=Sniffing, args=(dev,)))
    
    # starting the threads to work
    for thread in threads:
        thread.start()
        time.sleep(0.1)

#this is how to run part B, make sure you run it as root.
# PSDetect()