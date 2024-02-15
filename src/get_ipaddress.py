import socket

def get_ip_address():
    """Get the primary local IP address of the machine."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.connect(('10.255.255.255', 1))  # This IP does not need to be reachable
            IP = s.getsockname()[0]
        except socket.error:
            IP = None  # or consider logging error or raising a custom exception
    return IP
