from binascii import unhexlify

ciphertext_hex = "6032746a643360617865696569606e6c725962686562616657636e6360676359767368607665707c696f667d606b685967726d5b65775749484e5d4d79"
key = b"too much coffee"
key_length = len(key)

# Step 1: Convert hex string to bytes
ciphertext = unhexlify(ciphertext_hex)

# Step 2: Decrypt the full ciphertext using the known key
decrypted_bytes = b''
for i in range(len(ciphertext)):
    decrypted_bytes += bytes([ciphertext[i] ^ key[i % key_length]])

print(decrypted_bytes.decode('ascii'))