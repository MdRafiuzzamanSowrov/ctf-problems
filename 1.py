import re

# Deobfuscation Functions
def deobfuscate1(string):
    mapping = {
        'a': 'n', 'b': 'o', 'c': 'p', 'd': 'q', 'e': 'r', 'f': 's', 'g': 't',
        'h': 'u', 'i': 'v', 'j': 'w', 'k': 'x', 'l': 'y', 'm': 'z',
        'n': 'a', 'o': 'b', 'p': 'c', 'q': 'd', 'r': 'e', 's': 'f', 't': 'g',
        'u': 'h', 'v': 'i', 'w': 'j', 'x': 'k', 'y': 'l', 'z': 'm',
        'A': 'N', 'B': 'O', 'C': 'P', 'D': 'Q', 'E': 'R', 'F': 'S', 'G': 'T',
        'H': 'U', 'I': 'V', 'J': 'W', 'K': 'X', 'L': 'Y', 'M': 'Z',
        'N': 'A', 'O': 'B', 'P': 'C', 'Q': 'D', 'R': 'E', 'S': 'F', 'T': 'G',
        'U': 'H', 'V': 'I', 'W': 'J', 'X': 'K', 'Y': 'L', 'Z': 'M',
        '0': '5', '1': '6', '2': '7', '3': '8', '4': '9',
        '5': '0', '6': '1', '7': '2', '8': '3', '9': '4',
        '_': '-', '-': '_'
    }
    return ''.join(mapping.get(c, c) for c in string)

def deobfuscate2(string):
    def reverse_alpha(c):
        if 'a' <= c <= 'z':
            return chr(ord('z') - (ord(c) - ord('a')))
        elif 'A' <= c <= 'Z':
            return chr(ord('Z') - (ord(c) - ord('A')))
        return c
    digit_map = {str(i): str(9 - i) for i in range(10)}
    symbol_map = {'_': '=', '=': '_', '-': '+', '+': '-'}
    result = []
    for c in string:
        if c.isalpha():
            result.append(reverse_alpha(c))
        elif c in digit_map:
            result.append(digit_map[c])
        elif c in symbol_map:
            result.append(symbol_map[c])
        else:
            result.append(c)
    return ''.join(result)

def deobfuscate3(string):
    def reverse_char(c):
        if 'a' <= c <= 'z':
            return chr(ord('z') - (ord(c) - ord('a')))
        elif 'A' <= c <= 'Z':
            return chr(ord('Z') - (ord(c) - ord('A')))
        elif '0' <= c <= '9':
            return str(9 - int(c))
        elif c == '_':
            return '*'
        elif c == '*':
            return '_'
        elif c == '-':
            return '!'
        elif c == '!':
            return '-'
        else:
            return c
    return ''.join(reverse_char(c) for c in string)

# Load the 1.py file
with open("1.py", "r", encoding="utf-8", errors="ignore") as f:
    code = f.read()

# Extract the data variable (big triple-quoted string)
data_match = re.search(r'data\s*=\s*"""\n(.*?)\n"""', code, re.DOTALL)
if not data_match:
    print("[-] Couldn't find the 'data' variable.")
    exit()

obfuscated_data = data_match.group(1)

# Decode step-by-step
step1 = deobfuscate1(obfuscated_data)
step2 = deobfuscate2(step1)
decoded_data = deobfuscate3(step2)

# Search for flag
flags = re.findall(r'SK-CERT\{.*?\}', decoded_data)

if flags:
    print("[✅] Found Flag:")
    for flag in flags:
        print(flag)
else:
    print("[-] No flag found.")
