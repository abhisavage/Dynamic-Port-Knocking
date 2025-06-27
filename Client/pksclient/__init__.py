from scapy.all import IP, TCP, send, sr1
from time import sleep
import socket

from .config import Config


def send_tcp_syn_packet(server: str, port: int) -> None:
    """Send a TCP SYN packet to the specified server and port."""
    # Create SYN packet with explicit flags
    pkt = IP(dst=server)/TCP(dport=port, flags='S', sport=12345)
    
    # Send packet with verbose output disabled
    # Using send() for fire-and-forget
    send(pkt, verbose=False)
    
    print(f"Sent SYN packet to {server}:{port}")


def send_tcp_syn_packet_alternative(server: str, port: int) -> None:
    """Alternative method using sr1 for more reliable delivery."""
    # Create SYN packet
    pkt = IP(dst=server)/TCP(dport=port, flags='S', sport=12345)
    
    # Send and receive one response (sr1) - this ensures packet is actually sent
    try:
        response = sr1(pkt, timeout=1, verbose=False)
        print(f"Sent SYN packet to {server}:{port} - Response: {'Received' if response else 'No response'}")
    except Exception as e:
        print(f"Error sending to {server}:{port}: {e}")


def test_connectivity(server: str) -> bool:
    """Test basic connectivity to the server."""
    try:
        # Try to resolve the hostname/IP
        socket.gethostbyname(server)
        print(f"✓ Server {server} is reachable")
        return True
    except socket.gaierror:
        print(f"✗ Cannot resolve server {server}")
        return False


def main() -> None:
    print("Port Knock Sequence Client")
    print("=" * 30)
    
    # Test connectivity first
    if not test_connectivity(Config.server):
        input("Press enter to exit...")
        return
    
    # Get ports from user
    ports = []
    for n in ["first", "second", "third"]:
        while True:
            try:
                port = int(input(f"Please enter {n} port:\n> "))
                if 1 <= port <= 65535:
                    ports.append(port)
                    break
                else:
                    print("Port must be between 1 and 65535")
            except ValueError:
                print("Please enter a valid number")
    
    print(f"\nSending knock sequence to {Config.server}: {' -> '.join(map(str, ports))}")
    
    # Send the knock sequence
    for i, port in enumerate(ports, 1):
        print(f"Knock {i}/3: ", end="")
        send_tcp_syn_packet(Config.server, port)
        
        # Add delay between knocks (but not after the last one)
        if i < len(ports):
            sleep(0.5)  # Increased delay for better reliability
    
    print(f"\n✓ Knock sequence completed!")
    print(f"If the sequence is correct, port {Config.target_port} should be open for 60 seconds.")
    print(f"You can now connect to {Config.server}:{Config.target_port}")
    
    # Wait for the port to close
    print("\nWaiting for port to close...")
    sleep(60)
    
    print(f"Port {Config.target_port} is now closed.")
    input("Press enter to exit...")


# Alternative main function using sr1 for more reliable packet delivery
def main_alternative() -> None:
    """Alternative main function using sr1 for better reliability."""
    print("Port Knock Sequence Client (Alternative Method)")
    print("=" * 45)
    
    # Test connectivity first
    if not test_connectivity(Config.server):
        input("Press enter to exit...")
        return
    
    # Get ports from user
    ports = []
    for n in ["first", "second", "third"]:
        while True:
            try:
                port = int(input(f"Please enter {n} port:\n> "))
                if 1 <= port <= 65535:
                    ports.append(port)
                    break
                else:
                    print("Port must be between 1 and 65535")
            except ValueError:
                print("Please enter a valid number")
    
    print(f"\nSending knock sequence to {Config.server}: {' -> '.join(map(str, ports))}")
    
    # Send the knock sequence using sr1
    for i, port in enumerate(ports, 1):
        print(f"Knock {i}/3: ", end="")
        send_tcp_syn_packet_alternative(Config.server, port)
        
        # Add delay between knocks (but not after the last one)
        if i < len(ports):
            sleep(0.5)
    
    print(f"\n✓ Knock sequence completed!")
    print(f"If the sequence is correct, port {Config.target_port} should be open for 60 seconds.")
    print(f"You can now connect to {Config.server}:{Config.target_port}")
    
    # Wait for the port to close
    print("\nWaiting for port to close...")
    sleep(60)
    
    print(f"Port {Config.target_port} is now closed.")
    input("Press enter to exit...")


if __name__ == "__main__":
    # Try the standard method first, if issues persist, use the alternative
    main()
    # Uncomment the line below and comment the line above to use alternative method
    # main_alternative()