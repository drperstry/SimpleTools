import json
import socket
import argparse
import textwrap
from tkinter.tix import Tree

# Client and server agrees on p and g

def diffie_hellman_client(a, ip='127.0.0.1', port=50000):

    # Create a TCP/IP socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print ("Socket successfully created")
    except socket.error as err:
        print ("socket creation failed with error %s" %(err))

    # Connect the socket to the port where the server is listening
    server_address = (ip, port)
    print('connecting to %s port %s'% server_address)
    sock.connect(server_address)

    # Look for the response
    while True:
        data = sock.recv(1024)
        break

    # select a then send A= g**a mod p to server
    data=json.loads(data)
    g=data["g"]
    p=data["p"]
    B=data["B"]
    
    A=(g**a)%p
    A=str(A)
    sock.sendall(bytes(A, 'UTF-8'))
    
    sock.close()
    return((int(B)**a)%p)


def main():
    desc=textwrap.dedent('''diffie_hellman_client:
            The client side in diffie_hellman Protocol
            [opts means optional]
            usage:
                1: python Client.py diffie_hellman [-h] --a ClientKey [opts] --IP OtherEndIP --PORT OtherEndPORT''')
                
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=desc)
    subparser=parser.add_subparsers(dest='Command')
    diffie_hellman=subparser.add_parser('diffie_hellman')

    diffie_hellman.add_argument("--a", '-A',type=int, help="--a ClientKey", required=True)
    diffie_hellman.add_argument("--IP", '-ip',type=str, help="--IP OtherEndIP", required=False)
    diffie_hellman.add_argument("--PORT", '-port',type=int, help="--PORT OtherEndPORT", required=False)


    args = parser.parse_args()

    if args.Command == None:
        print("choose one of those commands [diffie_hellman]")
    elif args.Command == 'diffie_hellman':
        if(args.IP and args.PORT):
            print('shared key is: '+str(diffie_hellman_client(args.a, args.IP, args.PORT)))
        else:
            print('shared key is: '+str(diffie_hellman_client(args.a)))


# Driver Code
if __name__ == '__main__' :
    # Calling main function
    main()