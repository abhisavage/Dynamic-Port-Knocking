from scapy.all import *
from time import sleep
import socket

from .config import Config


def send_tcp_packet(server: str, port: int) -> None:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect((server, port))
        s.close()
    except:
        pass


def main() -> None:
    ports = [int(input(f"Please enter {n} port:\n>")) for n in ["first", "second", "third"]]

    for port in ports:
        send_tcp_packet(Config.server, port)
        sleep(0.1)

    print(f"The port {Config.target_port} should be open, you have 30 seconds to connect.")

    sleep(30)

    input(f"The port {Config.target_port} is now closed. Press enter to close this window...")
