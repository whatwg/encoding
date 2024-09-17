# Largely copied from tools-index.py to help create a table for GB18030-2022 mappings.

import os

if not os.path.exists("UnicodeData.txt"):
  # Download UnicodeData.txt if it doesn't exist yet
  open("UnicodeData.txt", "w").write(requests.get("https://unicode.org/Public/UNIDATA/UnicodeData.txt").text)

names = open("UnicodeData.txt", "r").readlines()

data = [("82359037", 0x9FB4),
("82359038", 0x9FB5),
("82359039", 0x9FB6),
("82359130", 0x9FB7),
("82359131", 0x9FB8),
("82359132", 0x9FB9),
("82359133", 0x9FBA),
("82359134", 0x9FBB),
("84318236", 0xFE10),
("84318237", 0xFE11),
("84318238", 0xFE12),
("84318239", 0xFE13),
("84318330", 0xFE14),
("84318331", 0xFE15),
("84318332", 0xFE16),
("84318333", 0xFE17),
("84318334", 0xFE18),
("84318335", 0xFE19)]

def format_cp(cp):
    return "U+" + hex(cp)[2:].rjust(4, "0").upper()

def get_name(cp):
    if cp >= 0x3400 and cp <= 0x4DB5:
        return "<CJK Ideograph Extension A>"
    elif cp >= 0x4E00 and cp <= 0x9FCB:
        return "<CJK Ideograph>"
    elif cp >= 0xAC00 and cp <= 0xD7A3:
        #return "<Hangul Syllable>"
        i = cp - 0xAC00
        s = jamo[0][i//28//21] + jamo[1][i//28%21] + jamo[2][i%28]
        return "HANGUL SYLLABLE " + s
    elif cp >= 0xE000 and cp <= 0xF8FF:
        return "<Private Use>"
    elif cp >= 0x20000 and cp <= 0x2A6D6:
        return "<CJK Ideograph Extension B>"
    elif cp >= 0x2A700 and cp <= 0x2B734:
        return "<CJK Ideograph Extension C>"
    elif cp >= 0x2B740 and cp <= 0x2B81D:
        return "<CJK Ideograph Extension D>"

    index = format_cp(cp)[2:] + ";"
    for line in names:
        if line.startswith(index):
            return (line.split(";"))[1]

    print("name not found", format_cp(cp)[2:])
    return "<Private Use>"

for bytes_as_string, code_point in data:

    split_bytes = [bytes_as_string[i:i+2] for i in range(0, len(bytes_as_string), 2)]

    print("     <tr>")

    for byte in split_bytes:
        print(f"      <td>0x{byte}")

    print(f"      <td>{format_cp(code_point)}")
    print(f"      <td>{chr(code_point)} ({get_name(code_point)})")
