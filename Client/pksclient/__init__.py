from scapy.all import IP, TCP, send
from time import sleep
import socket

from .config import Config


def send_tcp_packet(server: str, port: int) -> None:
    pkt = IP(dst=server)/TCP(dport=port, flags='S')
    send(pkt, verbose=False)


def main() -> None:
    ports = [int(input(f"Please enter {n} port:\n>")) for n in ["first", "second", "third"]]

    for port in ports:
        send_tcp_packet(Config.server, port)
        sleep(0.2)  # Slightly longer delay for reliability

    print(f"If the sequence is correct, the port {Config.target_port} should be open, you have 60 seconds to connect.")

    sleep(60)

    input(f"The port {Config.target_port} is now closed. Press enter to close this window...")
