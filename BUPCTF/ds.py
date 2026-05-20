#!/usr/bin/env python3
# deep_scan.py — aggressive scanner for the flag_checker challenge
from pathlib import Path
import sys
import itertools
import string

data = Path("flag_checker").read_bytes()
L = len(data)

# known items from your dump
alphabet = b'BUPCTF{}_-?R3NJOYgh1s7E'    # from 0x3110
table = bytes.fromhex("031c11021d0f211369056b12050f1c1705136b2e296d0565050c370b6a180513")
tlen = len(table)
assert tlen == 32

PRINT_MIN = 8   # minimum printable length to show
ALPH = alphabet

def is_printable(b):
    return all(32 <= c < 127 for c in b)

def likely_flag_bytes(b):
    # look for CTF-looking pattern
    if b'BUPCTF{' in b: 
        return True
    # or any printable containing braces and at least PRINT_MIN chars
    if b'{' in b and b'}' in b and is_printable(b) and len(b) >= PRINT_MIN:
        return True
    return False

def scan_xor_add_sub(window_size=32, step=1, rotations=True, repeat_key=True):
    seen = 0
    for off in range(0, L - window_size + 1, step):
        win = data[off:off+window_size]
        if repeat_key and tlen != window_size:
            # create key by repeating/truncating table
            rep = (table * ((window_size // tlen) + 1))[:window_size]
        else:
            rep = table[:window_size]
        # try rotated table variants (if requested)
        rots = [rep]
        if rotations:
            for r in range(1, min(8, len(rep))):  # try small rotations
                rots.append(rep[r:]+rep[:r])
        for key in rots:
            # XOR
            x = bytes([win[i] ^ key[i] for i in range(window_size)])
            if likely_flag_bytes(x):
                print(f"XOR  size={window_size} off=0x{off:x} keyrotlen={len(key)} -> {x!r}")
                seen += 1
            # ADD / SUB
            a = bytes([(win[i] + key[i]) & 0xff for i in range(window_size)])
            s = bytes([(win[i] - key[i]) & 0xff for i in range(window_size)])
            if likely_flag_bytes(a):
                print(f"ADD  size={window_size} off=0x{off:x} -> {a!r}")
                seen += 1
            if likely_flag_bytes(s):
                print(f"SUB  size={window_size} off=0x{off:x} -> {s!r}")
                seen += 1
    return seen

def scan_table_as_indices(max_base_scan=0x200000):
    # Interpret the table as offsets (indices) to pick bytes from data at base+table[i],
    # or as (base + table[i]) modulo filelen. Then see if that maps into printable / alphabet indices.
    seen = 0
    limit = min(L, max_base_scan)
    for base in range(0, limit, 1):
        try:
            picked = bytes([ data[(base + table[i]) % L] for i in range(tlen) ])
        except Exception:
            continue
        # try mapping each picked byte into alphabet by modulo or direct compare
        # 1) If picked bytes are small (<len(ALPH)) treat as indices
        if all(pb < len(ALPH) for pb in picked):
            mapped = bytes([ ALPH[pb] for pb in picked ])
            if likely_flag_bytes(mapped):
                print(f"IDX1 base=0x{base:x} -> {mapped!r}")
                seen += 1
        # 2) If picked bytes look printable, show them
        if is_printable(picked[:PRINT_MIN]):
            if likely_flag_bytes(picked):
                print(f"PICK base=0x{base:x} -> {picked!r}")
                seen += 1
        # 3) try XOR between picked and table
        x = bytes([picked[i] ^ table[i] for i in range(tlen)])
        if likely_flag_bytes(x):
            print(f"IDX_XOR base=0x{base:x} -> {x!r}")
            seen += 1
    return seen

def scan_rotating_vigenere(window_size=32, step=1):
    # try win[i] +/- table[(i+k) % tlen] for k offsets
    seen = 0
    for off in range(0, L - window_size + 1, step):
        win = data[off:off+window_size]
        for k in range(0, tlen):
            key = table[k:k+window_size] + table[:max(0, k+window_size - tlen)]
            key = key[:window_size]
            s = bytes([(win[i] - key[i]) & 0xff for i in range(window_size)])
            if likely_flag_bytes(s):
                print(f"VIG_SUB off=0x{off:x} k={k} -> {s!r}")
                seen += 1
            x = bytes([win[i] ^ key[i] for i in range(window_size)])
            if likely_flag_bytes(x):
                print(f"VIG_XOR off=0x{off:x} k={k} -> {x!r}")
                seen += 1
    return seen

def quick_small_windows():
    # also check small windows 8..48
    seen = 0
    for w in range(8, 48, 1):
        s = scan_xor_add_sub(window_size=w, step=1, rotations=True, repeat_key=True)
        seen += s
    return seen

def main():
    total = 0
    print("== Stage A: scan XOR/ADD/SUB with 32-byte key (rotations/repeat) ==")
    total += scan_xor_add_sub(window_size=32, step=1)
    print("== Stage B: scan smaller/larger windows (8..48) ==")
    total += quick_small_windows()
    print("== Stage C: interpret table as indices into file (base+table) ==")
    total += scan_table_as_indices(max_base_scan=0x20000)  # change limit if desired
    print("== Stage D: rotating vigenere-like attempts ==")
    total += scan_rotating_vigenere(window_size=32, step=1)
    if total == 0:
        print("No obvious candidates found. Next steps:")
        print("- Increase index scan range in scan_table_as_indices(max_base_scan=...)")
        print("- Try searching for shorter flag length (e.g. 16) and try table reused as multi-block key")
        print("- Provide output of 'readelf -S flag_checker' and '.rodata' hexdump 'readelf -x .rodata flag_checker' so I can map file offsets -> VA and find code references.")
    else:
        print(f"Found {total} candidate(s). Paste them here and I will decode exactly.")

if __name__ == '__main__':
    main()
