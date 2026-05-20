def z1x(n):
    a1b = 0
    for c in (range(1, n + 1)):
        a1b += pow(c, 2) + c  
    return 0.5 * a1b

def q3m(a, n, r):
    p0x = 0
    v1z = a
    for j in range(n):
        p0x = p0x + v1z
        v1z = v1z * r
        print(v1z)
    return p0x

flag = "bcsctf2025{fake_flag}"

m4n = 8973496431337
e8d = list()

for k in range(len(flag)):
    y2v = z1x(q3m(1, ord(flag[k]), 3) * m4n)
    e8d.append(y2v ^ m4n)

print(e8d)
