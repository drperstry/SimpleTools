import nmap

def ScanPort80(host):
    port='80'
    nmapcan = nmap.PortScanner()
    try:
        nmapcan.scan(host,port)
    except:
        print('make sure to write a correct ip target')
    print('Host : %s' % (host))
    print('State : %s' % nmapcan[host].state())
    print('----------')
    print('port 80 state: %s' % (nmapcan[host]["tcp"][int(80)]['state']))

# here add the ip  
ScanPort80('127.0.0.1')
