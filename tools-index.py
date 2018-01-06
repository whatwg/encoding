from ftplib import FTP
import os
import json

data = json.loads(open("indexes.json", "r").read())

if not os.path.exists("UnicodeData.txt"):
  # Download UnicodeData.txt via FTP if it doesn't exist yet
  ftp = FTP("ftp.unicode.org")
  ftp.login()
  ftp.retrbinary("RETR /Public/UNIDATA/UnicodeData.txt", open("UnicodeData.txt","wb").write)
  ftp.quit()

names = open("UnicodeData.txt", "r").readlines()

jamo = [
  ["G","GG","N","D","DD","R","M","B","BB","S","SS","","J","JJ","C","K","T","P","H"],
  ["A","AE","YA","YAE","EO","E","YEO","YE","O","WA","WAE","OE","YO","U","WEO","WE","WI","YU","EU","YI","I"],
  ["","G","GG","GS","N","NJ","NH","D","L","LG","LM","LB","LS","LT","LP","LH","M","B","BS","S","SS","NG","J","C","K","T","P","H"]
]

def char(cp):
    if cp > 0xFFFF:
        hi, lo = divmod(cp-0x10000, 0x400)
        return unichr(0xD800+hi) + unichr(0xDC00+lo)
    return unichr(cp)

def format_index(num, width):
    return str(num).rjust(width, " ")

def format_cp(cp):
    return "0x" + hex(cp)[2:].rjust(4, "0").upper()

def get_name(cp):
    if cp >= 0x3400 and cp <= 0x4DB5:
        return "<CJK Ideograph Extension A>"
    elif cp >= 0x4E00 and cp <= 0x9FCB:
        return "<CJK Ideograph>"
    elif cp >= 0xAC00 and cp <= 0xD7A3:
        #return "<Hangul Syllable>"
        i = cp - 0xAC00
        s = jamo[0][i/28/21] + jamo[1][i/28%21] + jamo[2][i%28]
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

    print "name not found", format_cp(cp)[2:]
    return "<Private Use>"

for index in data:
    import codecs, hashlib, datetime
    handle = codecs.open("index-" + index + ".txt", "w", "utf-8")
    handle.write("# For details on index index-" + index + ".txt see the Encoding Standard\n")
    handle.write("# https://encoding.spec.whatwg.org/\n")
    handle.write("#\n")
    handle.write("# Identifier: " + hashlib.sha256(str(data[index])).hexdigest() + "\n")
    handle.write("# Date: " + str(datetime.date.today()) + "\n")
    handle.write("\n")

    # gb18030-ranges is not like the other indexes, it's an index of ranges
    if index == "gb18030-ranges":
        for range in data[index]:
            handle.write(format_index(range[0], 6) + "\t" + format_cp(range[1]) + "\n")
        continue

    i = 0
    width = len(str(len(data[index])))
    for cp in data[index]:
        if cp != None:
            name = get_name(cp)
            handle.write(format_index(i, width) + "\t" + format_cp(cp) + "\t" + char(cp) + " (" + name + ")\n")
        i += 1
