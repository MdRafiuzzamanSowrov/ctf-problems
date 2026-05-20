def decrypt(cipher, a, b, p=97, g=31, text_key="trudeau"):
    # Regenerate keys
    u = pow(g, a, p)
    v = pow(g, b, p)
    shared_key = pow(v, a, p)
    print(f"[+] Shared key: {shared_key}")

    # Step 1: Reverse multiplicative encryption
    plain_ord = [val // (shared_key * 311) for val in cipher]
    semi_plain = ''.join(chr(c) for c in plain_ord)

    # Step 2: Reverse XOR (dynamic_xor_encrypt was on reversed input)
    key_len = len(text_key)
    decrypted = ""
    for i, char in enumerate(semi_plain):
        key_char = text_key[i % key_len]
        decrypted_char = chr(ord(char) ^ ord(key_char))
        decrypted = decrypted_char + decrypted  # reversed back

    return decrypted


if __name__ == "__main__":
    cipher = [97965, 185045, 740180, 946995, 1012305, 21770, 827260, 751065, 718410, 457170, 0, 903455, 228585, 54425, 740180, 0, 239470, 936110, 10885, 674870, 261240, 293895, 65310, 65310, 185045, 65310, 283010, 555135, 348320, 533365, 283010, 76195, 130620, 185045]
    a = 88
    b = 26
    flag = decrypt(cipher, a, b)
    print(f"[+] Decrypted message: {flag}")
