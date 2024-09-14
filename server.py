import socket, stun, zhmiscellany


zhmiscellany.misc.die_on_key()


def get_external_ip():
    # Use a specific STUN server
    stun_server = ('stun.l.google.com', 19302)
    nat_type, external_ip, external_port = stun.get_ip_info(stun_host=stun_server[0], stun_port=stun_server[1])

    if external_ip is None or external_port is None:
        print("Failed to get external IP and port.")
    else:
        print(f"External IP: {external_ip}, External Port: {external_port}")

    return external_ip, external_port


def run_server():
    external_ip, external_port = get_external_ip()

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind to the external IP and port
    sock.bind(('', external_port))
    print(f"Server listening on {external_ip}:{external_port}")

    # Wait for a client to connect
    while True:
        data, addr = sock.recvfrom(1024)
        print(f"Received message from {addr}: {data.decode()}")
        sock.sendto(b"Hello from the server!", addr)


if __name__ == "__main__":
    run_server()
