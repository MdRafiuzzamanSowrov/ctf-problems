#!/usr/bin/env python3
# Universal Hatagawa-family solver (fixed indentation + __main__ guard):
#  - Single-connection multi-sample capture
#  - Z3 bit-vector SMT
#  - Tries byte-order {BE, LE} and discard {0,1,2} extra states/call
#  - Self-verifies before printing candidates
#
# Usage:
#   pip3 install z3-solver  # or: sudo apt-get -y install python3-z3
#   python3 flag_fixed.py <host> <port> --samples 10

import re, socket, argparse, sys
from typing import List, Tuple, Optional
from z3 import BitVec, BitVecVal, Solver, Extract, sat

PROMPT = b'|  > '
CIPH_RE = re.compile(br'([A-Za-z0-9_]+)\{([0-9a-fA-F]+)\}')

def recv_until(sock, marker: bytes, max_bytes: int = 1_000_000) -> bytes:
    buf = b""
    while marker not in buf:
        chunk = sock.recv(4096)
        if not chunk:
            break
        buf += chunk
        if len(buf) > max_bytes:
            break
    return buf

def fetch_samples(host: str, port: int, samples: int) -> Tuple[str, List[bytes]]:
    s = socket.create_connection((host, port), timeout=8)
    recv_until(s, PROMPT)
    outs = []
    prefix = None
    for _ in range(samples):
        s.sendall(b's\n')
        data = recv_until(s, PROMPT)
        m = CIPH_RE.search(data)
        if not m:
            raise RuntimeError("Could not find <PREFIX>{<hex>} in output.")
        cur_prefix = m.group(1).decode()
        if prefix is None:
            prefix = cur_prefix
        elif prefix != cur_prefix:
            raise RuntimeError(f"Prefix changed mid-connection: {prefix} -> {cur_prefix}")
        outs.append(bytes.fromhex(m.group(2).decode()))
    try:
        s.sendall(b'w\n')
    except Exception:
        pass
    s.close()
    L = len(outs[0])
    if not all(len(x) == L for x in outs):
        raise RuntimeError("Ciphertext lengths differ; unexpected.")
    return prefix, outs

def extract_byte(state_bv, i, endian: str):
    # endian = 'be' or 'le'
    # Return the i-th byte (0..7) in the chosen endianness.
    if endian == 'be':
        hi = 63 - 8*i
        lo = 56 - 8*i
    else:  # 'le'
        hi = 8*i + 7
        lo = 8*i
    return Extract(hi, lo, state_bv)

def solve_with(endian: str, discard: int, cts: List[bytes]):
    L = len(cts[0])
    full_blocks = L // 8
    last_bytes  = L % 8

    BV64 = lambda name: BitVec(name, 64)
    BV8  = lambda name: BitVec(name, 8)
    BVV64 = lambda x: BitVecVal(x & ((1<<64)-1), 64)

    a  = BV64('a')
    c  = BV64('c')
    s1 = BV64('s1')                  # first state used for first sample
    m  = [BV8(f'm_{i}') for i in range(L)]  # plaintext bytes

    S = Solver()
    # Generator constraints from challenge family:
    S.add((a & BVV64(7)) == BVV64(5))    # a % 8 == 5
    S.add((c & BVV64(1)) == BVV64(1))    # c is odd

    def step(x):  # modulo 2^64 by bit-vector wrap
        return a * x + c

    state = s1
    for sample in cts:
        idx = 0
        # consume full 8-byte states
        for _ in range(full_blocks):
            for b in range(8):
                S.add(m[idx] ^ extract_byte(state, b, endian) == BitVecVal(sample[idx], 8))
                idx += 1
            state = step(state)
        # consume partial state
        if last_bytes != 0:
            for b in range(last_bytes):
                S.add(m[idx] ^ extract_byte(state, b, endian) == BitVecVal(sample[idx], 8))
                idx += 1
            state = step(state)
        # discard extra generated states per call
        for _ in range(discard):
            state = step(state)

    if S.check() != sat:
        return None
    M = S.model()
    aa  = M[a].as_long()  & ((1<<64)-1)
    cc  = M[c].as_long()  & ((1<<64)-1)
    ss1 = M[s1].as_long() & ((1<<64)-1)
    pt  = bytes(int(M[m[i]].as_long() & 0xFF) for i in range(L))
    return aa, cc, ss1, pt

def verify_combo(a: int, c: int, s1: int, pt: bytes, cts: List[bytes], endian: str, discard: int) -> bool:
    L = len(pt)
    full_blocks = L // 8
    last_bytes  = L % 8

    def step(x): return (a * x + c) & ((1<<64)-1)

    def bytes_from_state(st, endian):
        b = st.to_bytes(8, 'big')
        return b if endian == 'be' else b[::-1]

    state = s1
    for ct in cts:
        ks = bytearray()
        st = state
        for _ in range(full_blocks):
            ks += bytes_from_state(st, endian)
            st = step(st)
        if last_bytes != 0:
            ks += bytes_from_state(st, endian)[:last_bytes]
            st = step(st)
        for _ in range(discard):
            st = step(st)

        if bytes([pt[i] ^ ks[i] for i in range(L)]) != ct:
            return False
        state = st
    return True

def main():
    ap = argparse.ArgumentParser(description="Universal Hatagawa-family solver (auto endian/discard).")
    ap.add_argument("host")
    ap.add_argument("port", type=int)
    ap.add_argument("--samples", type=int, default=10)
    args = ap.parse_args()

    print(f"[+] Connecting to {args.host}:{args.port} and collecting {args.samples} ciphertexts...")
    prefix, cts = fetch_samples(args.host, args.port, args.samples)
    print(f"[+] Prefix: {prefix}")
    print(f"[+] Collected {len(cts)} samples, each {len(cts[0])} bytes.")

    tried = []
    for endian in ("be", "le"):
        for discard in (0, 1, 2):
            print(f"[*] Trying endian={endian.upper()} discard={discard} ...", flush=True)
            res = solve_with(endian, discard, cts)
            if res is None:
                print("    -> UNSAT")
                tried.append((endian, discard, False, None))
                continue
            a, c, s1, pt = res
            ok = verify_combo(a, c, s1, pt, cts, endian, discard)
            print(f"    -> {'OK' if ok else 'MISMATCH'} | a=0x{a:016x} c=0x{c:016x} s1=0x{s1:016x}")
            tried.append((endian, discard, ok, pt if ok else None))
            if ok:
                hex_lower = pt.hex()
                hex_upper = hex_lower.upper()
                print("\n[=] Submit one of these EXACTLY:")
                print(f"  1) {prefix}{{{hex_lower}}}")
                print(f"  2) {prefix}{{{hex_upper}}}")
                try:
                    ascii_guess = pt.decode('ascii')
                    if ascii_guess.isprintable():
                        print(f"  3) {prefix}{{{ascii_guess}}}    # ASCII")
                except Exception:
                    pass
                return

    print("\n[!] No verified combination worked. Summary:")
    for endian, discard, ok, _ in tried:
        print(f"    endian={endian.upper()} discard={discard}: {'OK' if ok else 'FAIL'}")
    print("[i] Try increasing --samples, and re-run in a fresh connection.")
    sys.exit(2)

if __name__ == "__main__":
    main()
