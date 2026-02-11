import argparse
import sys
import textwrap
import time
from functools import partial
import threading

import nmap
from scapy.all import sniff, get_if_addr, get_working_ifaces


def scan_ports(host, ports="1-1024"):
    """Scan specified ports on a target host using nmap."""
    scanner = nmap.PortScanner()
    try:
        scanner.scan(host, ports)
    except nmap.PortScannerError as e:
        print(f"Scan error: {e}", file=sys.stderr)
        return

    print(f"Host: {host}")
    print(f"State: {scanner[host].state()}")
    print("-" * 40)

    for proto in scanner[host].all_protocols():
        port_list = sorted(scanner[host][proto].keys())
        for port in port_list:
            state = scanner[host][proto][port]["state"]
            print(f"  {proto}/{port}: {state}")


def _analyze_packet(pkt_dict, if_ip, pkt):
    """Analyze a packet and detect port scanning behavior."""
    if "IP" not in pkt:
        return

    ip = pkt["IP"].src
    port = None

    if "TCP" in pkt:
        port = pkt["TCP"].dport
    elif "UDP" in pkt:
        port = pkt["UDP"].dport

    if pkt["IP"].dst != if_ip or port is None:
        return

    now = time.time()

    if ip not in pkt_dict:
        pkt_dict[ip] = {"prevPort": -2, "timer": now, "counter": 1}
        return

    record = pkt_dict[ip]

    if now - record["timer"] > 5:
        pkt_dict[ip] = {"prevPort": port, "timer": now, "counter": 1}
        return

    if port - 1 == record["prevPort"]:
        record["prevPort"] = port
        record["counter"] += 1
        record["timer"] = now
        if record["counter"] >= 15:
            print(f"Scan detected. The scanner originated from host {ip}")
            del pkt_dict[ip]
    else:
        pkt_dict[ip] = {"prevPort": port, "timer": now, "counter": 1}


def _sniff_interface(dev):
    """Sniff packets on a single network interface."""
    pkt_dict = {}
    try:
        ip = get_if_addr(dev)
    except OSError:
        return
    sniff(filter="ip", iface=dev, prn=partial(_analyze_packet, pkt_dict, ip))


def detect_scan():
    """Listen on all network interfaces to detect port scanning activity.

    Must be run with root/administrator privileges.
    """
    devs = get_working_ifaces()
    threads = []

    for dev in devs:
        t = threading.Thread(target=_sniff_interface, args=(dev,), daemon=True)
        threads.append(t)

    for t in threads:
        t.start()
        time.sleep(0.1)

    print("Listening for port scans on all interfaces... (Ctrl+C to stop)")
    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        print("\nStopped.")


def main():
    desc = textwrap.dedent("""\
        Network Scanner & Detector

        Scan ports on a target host or detect incoming port scans.

        Usage:
            python network_scanner.py scan --host 192.168.1.1 --ports 1-1024
            python network_scanner.py detect
    """)

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=desc,
    )
    subparsers = parser.add_subparsers(dest="command")

    # Scan subcommand
    scan_parser = subparsers.add_parser("scan", help="Scan ports on a target host")
    scan_parser.add_argument("--host", "-H", type=str, required=True, help="Target host IP address")
    scan_parser.add_argument("--ports", "-p", type=str, default="1-1024", help="Port range to scan (default: 1-1024)")

    # Detect subcommand
    subparsers.add_parser("detect", help="Detect incoming port scans (requires root)")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)
    elif args.command == "scan":
        scan_ports(args.host, args.ports)
    elif args.command == "detect":
        detect_scan()


if __name__ == "__main__":
    main()
