import socket
import sys

HOST = "reverse.diucybercon.com"
PORT = 11667
PASSWORD = "galaxy_map\n"
TIMEOUT = 8.0

def recv_until(sock, term=b'\n', timeout=8.0):
    sock.settimeout(timeout)
    data = b''
    try:
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            data += chunk
            # break if we see the terminating prompt or a likely banner end
            if term in data:
                # don't break immediately; attempt to read a bit more for multi-line output
                # but we keep it simple here
                break
    except socket.timeout:
        pass
    return data

def main():
    try:
        with socket.create_connection((HOST, PORT), timeout=TIMEOUT) as s:
            # receive initial banner/prompt
            banner = recv_until(s, term=b':', timeout=TIMEOUT)
            sys.stdout.write(banner.decode(errors='replace'))
            # send password
            s.sendall(PASSWORD.encode())
            # read reply — try a bit longer
            reply = b''
            # read until socket closes or timeout
            s.settimeout(3.0)
            try:
                while True:
                    part = s.recv(4096)
                    if not part:
                        break
                    reply += part
            except socket.timeout:
                pass
            sys.stdout.write("\n--- server response ---\n")
            sys.stdout.write(reply.decode(errors='replace'))
    except Exception as e:
        print("Connection error:", e)

if __name__ == "__main__":
    main()
