import socket
import argparse
import textwrap
import json
# Client and server agrees on p and g

def diffie_hellman_server(p, g, b, ip='127.0.0.1', port=50000):
    
    # Create a TCP/IP socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print ("Socket successfully created")
    except socket.error as err:
        print ("socket creation failed with error %s" %(err))

    # Bind the socket to the port
    server_address = (ip, port)
    print('Starting up TCP Server on %s port %s'%server_address)
    sock.bind(server_address)

    #select b then send B= g**b mod p
    B=(g**b)%p
    B=str(B)
    data={'B':B, 'p':p, 'g':g}
    data=json.dumps(data)
    # Listen for incoming connections
    sock.listen(1)
    while True:
        # Wait for a connection
        print('waiting for a new connection')
        connection, client_address = sock.accept()
        print('connection from', client_address)
        
        # send B and p and g
        print('sending message back to the client')
        connection.sendall(bytes(data, 'UTF-8'))
        # Receive A 
        while True:
            data = connection.recv(1024)
            connection.close()
            break
        break
    
    A=int(data)
    return  (A**b)%p


def main():

    desc=textwrap.dedent('''diffie_hellman_server:
            The server side in diffie_hellman Protocol
            [opts means optional]
            usage:
                1: python Server.py diffie_hellman [-h] --p p --g g --b ServerKey [opts] --IP OtherEndIP --PORT OtherEndPORT''')
                
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=desc)
    subparser=parser.add_subparsers(dest='Command')
    diffie_hellman=subparser.add_parser('diffie_hellman')

    diffie_hellman.add_argument("--p", '-P',type=int, help="--p p", required=True)
    diffie_hellman.add_argument("--g", '-G',type=int, help="--g g", required=True)
    diffie_hellman.add_argument("--b", '-B',type=int, help="--b ServerKey", required=True)
    diffie_hellman.add_argument("--IP", '-ip',type=str, help="--IP OtherEndIP", required=False)
    diffie_hellman.add_argument("--PORT", '-port',type=int, help="--PORT OtherEndPORT", required=False)


    args = parser.parse_args()

    if args.Command == None:
        print("choose one of those commands [diffie_hellman]")
    elif args.Command == 'diffie_hellman':
        if(args.IP and args.PORT):
            print('shared key is: '+str(diffie_hellman_server(args.p, args.g, args.b, args.IP, args.PORT)))
        else:
            print('shared key is: '+str(diffie_hellman_server(args.p, args.g, args.b)))


# Driver Code
if __name__ == '__main__' :
    # Calling main function
    main()