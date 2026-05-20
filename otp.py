import socket

def xor_bytes(b1, b2):
    return bytes([a ^ b for a, b in zip(b1, b2)])

def main():
    host = "mercury.picoctf.net"
    port = 11188

    with socket.create_connection((host, port)) as s:
        # Step 1: Receive welcome and encrypted flag
        full_banner = s.recv(1024).decode()
        flag_line = s.recv(1024).decode()
        print(flag_line.strip())

        flag_enc_hex = flag_line.split("\n")[1].strip()
        flag_enc_bytes = bytes.fromhex(flag_enc_hex)

        # Step 2: Send the same encrypted flag back to get OTP key segment
        s.sendall(flag_enc_hex.encode() + b"\n")

        enc_response = s.recv(2048).decode()
        enc_input_hex = enc_response.split("\n")[1].strip()
        enc_input_bytes = bytes.fromhex(enc_input_hex)

        # Step 3: Derive keystream
        known_plaintext_bytes = bytes.fromhex(flag_enc_hex)
        key_stream = xor_bytes(known_plaintext_bytes, enc_input_bytes)

        # Step 4: Decrypt flag
        flag = xor_bytes(flag_enc_bytes, key_stream)

        try:
            print("\n[+] Decrypted Flag:", flag.decode())
        except:
            print("\n[!] Partial Flag (non-printables may exist):", flag)

if __name__ == "__main__":
    main()
