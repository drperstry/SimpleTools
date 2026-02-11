import json
import socket
import argparse
import textwrap
import sys


def run_server(p, g, b, ip="127.0.0.1", port=50000):
    """Start a Diffie-Hellman key exchange server."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except socket.error as err:
        print(f"Socket creation failed: {err}", file=sys.stderr)
        return None

    server_address = (ip, port)
    print(f"Starting Diffie-Hellman server on {ip}:{port}")
    sock.bind(server_address)

    B = pow(g, b, p)
    data = json.dumps({"B": str(B), "p": p, "g": g})

    sock.listen(1)
    try:
        print("Waiting for client connection...")
        connection, client_address = sock.accept()
        print(f"Connection from {client_address}")

        connection.sendall(data.encode("utf-8"))

        received = connection.recv(1024)
        connection.close()
    finally:
        sock.close()

    A = int(received)
    shared_key = pow(A, b, p)
    return shared_key


def run_client(a, ip="127.0.0.1", port=50000):
    """Connect to a Diffie-Hellman server and compute the shared key."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as err:
        print(f"Socket creation failed: {err}", file=sys.stderr)
        return None

    server_address = (ip, port)
    print(f"Connecting to {ip}:{port}")
    sock.connect(server_address)

    data = sock.recv(1024)
    params = json.loads(data)
    g = params["g"]
    p = params["p"]
    B = int(params["B"])

    A = pow(g, a, p)
    sock.sendall(str(A).encode("utf-8"))
    sock.close()

    shared_key = pow(B, a, p)
    return shared_key


def main():
    desc = textwrap.dedent("""\
        Diffie-Hellman Key Exchange

        Share a symmetric key between a client and server using the
        Diffie-Hellman protocol.

        Usage:
            python diffie_hellman.py server --p 23 --g 5 --b 6
            python diffie_hellman.py client --a 4
    """)

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=desc,
    )
    subparsers = parser.add_subparsers(dest="command")

    # Server subcommand
    server_parser = subparsers.add_parser("server", help="Run as DH server")
    server_parser.add_argument("--p", "-P", type=int, required=True, help="Prime number p")
    server_parser.add_argument("--g", "-G", type=int, required=True, help="Generator g")
    server_parser.add_argument("--b", "-B", type=int, required=True, help="Server secret key b")
    server_parser.add_argument("--ip", type=str, default="127.0.0.1", help="IP address (default: 127.0.0.1)")
    server_parser.add_argument("--port", type=int, default=50000, help="Port number (default: 50000)")

    # Client subcommand
    client_parser = subparsers.add_parser("client", help="Run as DH client")
    client_parser.add_argument("--a", "-A", type=int, required=True, help="Client secret key a")
    client_parser.add_argument("--ip", type=str, default="127.0.0.1", help="Server IP address (default: 127.0.0.1)")
    client_parser.add_argument("--port", type=int, default=50000, help="Server port (default: 50000)")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)
    elif args.command == "server":
        shared_key = run_server(args.p, args.g, args.b, args.ip, args.port)
        if shared_key is not None:
            print(f"Shared key: {shared_key}")
    elif args.command == "client":
        shared_key = run_client(args.a, args.ip, args.port)
        if shared_key is not None:
            print(f"Shared key: {shared_key}")


if __name__ == "__main__":
    main()
