from binascii import unhexlify

# Ciphertext (hex form)
hex_data = "65 6c ce 6b c1 75 61 7e 53 66 c9 52 d8 6c 6a 53 6e 6e de 52 df 63 6d 7e 75 7f ce 64 d5 63 73"
cipher = unhexlify(hex_data.replace(" ", ""))

# আমরা জানি flag সবসময় ictf{ দিয়ে শুরু হয়
known = b"ictf{"

# প্রথম len(known) bytes কে 'ictf{' এর সাথে XOR করে key বের করব
key = bytes([c ^ p for c, p in zip(cipher[:len(known)], known)])

# key রিপিট করে পুরো cipher এর সাথে XOR
full_key = (key * (len(cipher)//len(key)+1))[:len(cipher)]
plain = bytes([c ^ k for c, k in zip(cipher, full_key)])

print("Key (hex):", key.hex())
print("Plain:", plain.decode(errors="ignore"))
