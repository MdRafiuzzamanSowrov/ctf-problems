#!/usr/bin/env python3
from pathlib import Path
import sys

data = Path("flag_checker").read_bytes()

# the table you found (32 bytes)
table = bytes.fromhex("031c11021d0f211369056b12050f1c1705136b2e296d0565050c370b6a180513")
n = len(table)
assert n == 32

def printable(b):
    return all(32 <= c < 127 for c in b)

def check_window(off):
    win = data[off:off+n]
    if len(win) < n:
        return []
    cand = []
    # XOR
    x = bytes([win[i] ^ table[i] for i in range(n)])
    if b"BUPCTF{" in x or printable(x[:n]) and b"{" in x:
        cand.append(("XOR", off, x))
    # SUB (win - table)
    s = bytes([(win[i] - table[i]) & 0xff for i in range(n)])
    if b"BUPCTF{" in s or printable(s[:n]) and b"{" in s:
        cand.append(("SUB", off, s))
    # ADD (win + table)
    a = bytes([(win[i] + table[i]) & 0xff for i in range(n)])
    if b"BUPCTF{" in a or printable(a[:n]) and b"{" in a:
        cand.append(("ADD", off, a))
    return cand

# scan whole file
found = 0
for off in range(0, len(data)-n+1):
    res = check_window(off)
    if res:
        for typ, off0, val in res:
            print(f"{typ} @ 0x{off0:x}: {val!r}")
            found += 1

if found == 0:
    print("No obvious candidates found with simple XOR/ADD/SUB on 32-byte windows.")
    print("Next steps: (1) try other alignment sizes (16/24/48 bytes), (2) try rotating/offsetting the table,")
    print("(3) search separately for shorter printable results (flag could be shorter than 32 bytes).")
