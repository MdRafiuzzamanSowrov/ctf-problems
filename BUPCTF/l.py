# decode_try.py
from pathlib import Path
import itertools, string

p = Path("flag_checker").read_bytes()

off = 0x3110
region = p[off: off+256]  # tune length if needed

# extract visible alphabet string at start (null-terminated)
alpha = region.split(b'\x00',1)[0]
print("Alphabet (raw):", alpha)

# find candidate table(s) after alphabet
# scan for repeating/semi-structured blocks (we saw at +0x40)
table = region[0x40:0x40+32]
print("Candidate table (hex):", table.hex())

# try mapping table values (interpreting as indices) into alphabet if values small
def try_index_map(tbl, alph):
    out = []
    for v in tbl:
        if v < len(alph):
            out.append(chr(alph[v]))
        else:
            out.append('.')
    return ''.join(out)

print("Index map attempt:", try_index_map(table, alpha))

# try XOR, ADD, SUB of table against following bytes in region; attempt all alignments
def printable(s):
    return all(32 <= b < 127 for b in s)

for align in range(0, 64):
    payload = region[0x40+32+align: 0x40+32+align+32]
    if len(payload) < 8:
        continue
    # XOR
    xored = bytes([payload[i] ^ table[i] for i in range(min(len(payload), len(table)))])
    if b'BUPCTF{' in xored or printable(xored):
        print("XOR align", align, xored)
    # ADD/SUB
    addd = bytes([(payload[i] - table[i]) & 0xff for i in range(min(len(payload), len(table)))])
    if b'BUPCTF{' in addd or printable(addd):
        print("SUB align", align, addd)
    add2 = bytes([(payload[i] + table[i]) & 0xff for i in range(min(len(payload), len(table)))])
    if b'BUPCTF{' in add2 or printable(add2):
        print("ADD align", align, add2)
