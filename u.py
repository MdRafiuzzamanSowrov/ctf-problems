#!/usr/bin/env python3
import os, subprocess, struct, sys

BIN = "/mnt/data/chal (3)"

def run(cmd):
    return subprocess.check_output(cmd, text=True)

print("[*] file / basic info")
print(run(["file", BIN]).strip())
print(run(["readelf", "-l", BIN]))

# readelf told us: rodata segment maps file offset 0x77000 -> vaddr 0x477000
RO_FILE_OFF = 0x77000
RO_VADDR = 0x477000
print("[*] rodata file offset:", hex(RO_FILE_OFF), "vaddr base:", hex(RO_VADDR))

data = open(BIN, "rb").read()
ro = data[RO_FILE_OFF:RO_FILE_OFF + 0x30000]   # dump 192k to be safe
open("rodata.dump", "wb").write(ro)
print("[*] wrote rodata.dump (use this in Ghidra/IDA)")

# find printable strings in rodata
import string
def printable_sequences(d, minlen=4):
    seq = b""
    off = None
    for i, b in enumerate(d):
        if chr(b) in string.printable and b != 0:
            if off is None:
                off = i
            seq += bytes([b])
        else:
            if off is not None and len(seq) >= minlen:
                yield off, seq.decode('latin1')
            seq = b""
            off = None
    if off is not None and len(seq) >= minlen:
        yield off, seq.decode('latin1')

print("[*] strings in rodata (offset relative to file):")
for off, s in printable_sequences(ro):
    print(hex(RO_FILE_OFF + off), s)

# hexdump and interpret as little-endian 4-byte ints from the suspected blob start
BLOB_START = 0x77098 - RO_FILE_OFF  # offset inside rodata where it seemed to start
print("[*] showing ints starting at", hex(RO_FILE_OFF + BLOB_START))
for i in range(0, 160):
    off = BLOB_START + i*4
    if off + 4 > len(ro):
        break
    val = struct.unpack("<i", ro[off:off+4])[0]
    print(hex(RO_FILE_OFF + off), ro[off:off+4].hex(), val)

