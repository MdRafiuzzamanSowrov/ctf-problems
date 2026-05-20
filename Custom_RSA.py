qwerty =  "abcdefghijklmnopqrstuvwxyz"
dvorak =  "axje.uidchtnmbrl'poygk,qf;"  # Dvorak layout

q2d = {q: d for q, d in zip(qwerty, dvorak)}

def convert(text):
    result = ""
    for c in text.lower():
        if c in q2d:
            result += q2d[c]
        elif c == "_":
            result += "_"  # keep underscores
        else:
            result += c  # keep symbols/brackets
    return result

s = "mabmy_lr_ut_jpf_mak_qdrwbj_euhs"
decoded = convert(s)
print("Blitz{" + decoded + "}")
