import json

data = json.loads(open("indexes.json", "r").read())

# Copy from ftp://ftp.unicode.org/Public/UNIDATA/UnicodeData.txt
names = open("UnicodeData.txt", "r").readlines()

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
        return "<Hangul Syllable>"
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
    import codecs
    handle = codecs.open("index-" + index + ".txt", "w", "utf-8")
    handle.write("# Any copyright is dedicated to the Public Domain.\n")
    handle.write("# http://creativecommons.org/publicdomain/zero/1.0/\n")
    handle.write("#\n")
    handle.write("# For details on index-" + index + ".txt see the Encoding Standard\n")
    handle.write("# http://dvcs.w3.org/hg/encoding/raw-file/tip/Overview.html\n\n")

    # gb18030 is not like the other indexes, it's an index of ranges
    if index == "gb18030":
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
