# -*- coding: UTF8 -*-

from scapy.all import *
from time import sleep
import socket

from .config import Config


def send_tcp_packet(server: str, port: int) -> None:
    """
    Send a TCP SYN packet to the specified server:port.

    :param str server: A server's address. IP or DNS name.
    :param int port: The port to connect to.
    """
    try:
        # Create a TCP socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        # Try to connect to the port
        s.connect((server, port))
        s.close()
    except:
        pass  # We don't care if the connection fails, we just want to send the SYN packet


def main() -> None:
    ports = [int(input(f"Please enter {n} port:\n>")) for n in ["first", "second", "third"]]

    for port in ports:
        send_tcp_packet(Config.server, port)
        sleep(0.1)

    print(f"The port {Config.target_port} should be open, you have 30 seconds to connect.")

    sleep(30)

    input(f"The port {Config.target_port} is now closed. Press enter to close this window...")
