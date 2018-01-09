#!/usr/bin/python

import json
import sys
import unicodedata

directory = ""
if len(sys.argv) == 2:
    directory = sys.argv[1]

indexes = json.load(open("indexes.json", "r"))

names_lengths_langs = [
    ("ibm866", 16, "ru"),
    ("iso-8859-2", 16, "pl"),
    ("iso-8859-3", 16, "tr"),
    ("iso-8859-4", 16, "et"),
    ("iso-8859-5", 16, "ru"),
    ("iso-8859-6", 16, "ar"),
    ("iso-8859-7", 16, "el"),
    ("iso-8859-8", 16, "he"),
    ("iso-8859-10", 16, "no"),
    ("iso-8859-13", 16, "et"),
    ("iso-8859-14", 16, "ga"),
    ("iso-8859-15", 16, "de"),
    ("iso-8859-16", 16, "pl"),
    ("koi8-r", 16, "ru"),
    ("koi8-u", 16, "uk"),
    ("macintosh", 16, "de"),
    ("windows-874", 16, "th"),
    ("windows-1250", 16, "pl"),
    ("windows-1251", 16, "ru"),
    ("windows-1252", 16, "de"),
    ("windows-1253", 16, "el"),
    ("windows-1254", 16, "tr"),
    ("windows-1255", 16, "he"),
    ("windows-1256", 16, "ar"),
    ("windows-1257", 16, "et"),
    ("windows-1258", 16, "vi"),
    ("x-mac-cyrillic", 16, "ru"),
    ("jis0208", 94, "ja"),
    ("jis0212", 94, "ja"),
    ("euc-kr", 190, "ko"),
    ("gb18030", 190, "zh-cn"),
    ("big5", 157, "zh-tw"),
]

# Lead offset one, lead offset two,
# trail offset one, trail offset two,
byte_rules = {
    "jis0208": (0xA1, None, 0xA1, None),
    "jis0212": (0xA1, None, 0xA1, None),
    "shift_jis": (0x81, 0xC1, 0x40, 0x41),
    "euc-kr": (0x81, None, 0x41, None),
    "gb18030": (0x81, None, 0x40, 0x41),
    "big5": (0x81, None, 0x40, 0x62),
}

big5_prefer_last = [
  0x2550,
  0x255E,
  0x2561,
  0x256A,
  0x5341,
  0x5345,
]


def classify(code_point):
    if code_point < 0x80:
        raise Error()
    if code_point < 0x800:
        return "mid"
    if code_point > 0xFFFF:
        return "astral"
    if code_point >= 0xE000 and code_point <= 0xF8FF:
        return "pua"
    return "upper"


def check_compatibility(code_point):
    if code_point >= 0xF900 and code_point <= 0xFAFF:
        return " compatibility"
    if code_point >= 0x3400 and code_point <= 0x4DB5:
        return " ext"
    return ""


def aria(code_point, contiguous, duplicate):
    label = None
    classification = classify(code_point)
    if classification == "mid":
        label = "Two bytes"
    elif classification == "upper":
        label = "Three bytes"
    elif classification == "pua":
        label = "Three bytes, Private Use"
    elif classification == "astral":
        label = "Four bytes"
    block = check_compatibility(code_point)
    if block == " compatibility":
        label += ", Compatibility Ideograph"
    elif block == " ext":
        label += "Ideograph Extension A"
    elif code_point >= 0x4E00 and code_point <= 0x9FD5:
        label += ", Unified Ideograph"
    elif code_point >= 0xAC00 and code_point <= 0xD7AF:
        label += ", Hangul"
    if contiguous:
        label += ", contiguous"
    if duplicate:
        label += ", duplicate"
    return label


def code_point_to_ustr(code_point):
    try:
        return unichr(code_point)
    except ValueError:
        # For narrow builds
        high = 0xD7C0 + (code_point >> 10)
        low = 0xDC00 + (code_point & 0x3FF)
        return unichr(high) + unichr(low)


def format_code_point(code_point):
    if code_point >= 0x80 and code_point < 0xA0:
        # HTML prohibits C1 controls
        # TODO draw some fancy SVG hex inside the square
        return "<svg width=16 height=16><rect x=1 y=1 width=14 height=14 stroke=black stroke-width=2 fill=none /></svg>"
    # Big5's Plane 2 stuff is non-combining, so let's deal with it first,
    # since it need special treatment in narrow Python.
    if code_point > 0xFFFF:
        return code_point_to_ustr(code_point)
    as_str = unichr(code_point)
    if unicodedata.combining(as_str) == 0:
        return as_str
    else:
        return " " + as_str


def format_index(name, row_length, lang, bmp, duplicates, byte_rule):
    out_file = open("%s%s.html" % (directory, name), "w")
    out_file.write(("<!DOCTYPE html><html lang=en><meta charset=utf-8><title>%s</title><link rel=stylesheet href=visualization.css type=text/css><h1>%s</h1><p class=note role=note>This table is not normative.<p><a href='%s-bmp.html'>BMP coverage</a><p><a href='./#visualization'>Legend</a><table><thead>") % (name, name, "jis0208" if name == "shift_jis" else name))
    dec_row_cell = False
    if byte_rule:
        (lead_one, lead_two, trail_one, trail_two) = byte_rule
        if not (name == "big5" or name == "shift_jis"):
            dec_row_cell = True
            out_file.write("<tr><td><td><td>")
            for i in xrange(row_length):
                trail = i + trail_one
                if trail_two and i >= 0x3F:
                    trail = i + trail_two
                if trail < 0xA1:
                    out_file.write("<th>")
                else:
                    out_file.write("<th>%d" % (trail - 0xA0))
            out_file.write("<tr><td><td><td>")
        else:
            out_file.write("<tr><td><td>")
        for i in xrange(row_length):
            trail = i + trail_one
            if trail_two and i >= 0x3F:
                trail = i + trail_two
            out_file.write("<th class=byte>%02X" % trail)
        if dec_row_cell:
            out_file.write("<tr><td><td><td>")
        else:
            out_file.write("<tr><td><td>")
    else:
        out_file.write("<tr><td>")
    for i in xrange(row_length):
        out_file.write("<th>%02X" % i)
    out_file.write("<tbody>")
    previous = None
    new_row = True
    pointer = 0
    row_num = 0
    astral_seen = set()
    if name == "shift_jis":
        name = "jis0208"
    index = indexes[name]
    for code_point in index:
        if new_row:
            out_file.write("<tr>")
            if byte_rule:
                (lead_one, lead_two, trail_one, trail_two) = byte_rule
                lead = row_num + lead_one
                if lead_two and row_num >= 0x1F:
                    lead = row_num + lead_two
                if dec_row_cell:
                    if lead < 0xA1:
                        out_file.write("<th>")
                    else:
                        out_file.write("<th>%d" % (lead - 0xA0))
                out_file.write("<th class=byte>%02X" % lead)
            out_file.write("<th>%02X" % row_num)
            new_row = False
        duplicate = False
        if code_point:
            if code_point < 0x10000:
                if bmp[code_point]:
                    duplicate = True
                    duplicates.add(code_point)
                    if code_point in big5_prefer_last:
                        bmp[code_point] = pointer
                else:
                    bmp[code_point] = pointer
            else:
                if code_point in astral_seen:
                    duplicate = True
                    duplicates.add(code_point)
                else:
                    astral_seen.add(code_point)
            contiguous = previous and previous + 1 == code_point
            out_file.write((u"<td class='%s %s%s%s' aria-label='%s'><dl><dt>%d<dd lang=%s>%s<dd>U+%04X</dl>" % ("contiguous" if contiguous else "discontiguous", classify(code_point), " duplicate" if duplicate else "", check_compatibility(code_point), aria(code_point, contiguous, duplicate), pointer, lang, format_code_point(code_point), code_point)).encode("utf-8"))
        else:
            out_file.write((u"<td class=unmapped aria-label=Unmapped><dl><dt>%d<dd>\uFFFD<dd>\u00A0</dl>" % pointer).encode("utf-8"))
        previous = code_point
        pointer += 1
        if pointer % row_length == 0:
            new_row = True
            row_num += 1
    out_file.write("</table>")
    out_file.close()


def format_coverage(name, lang, bmp, duplicates):
    out_file = open("%s%s-bmp.html" % (directory, name), "w")
    out_file.write(("<!DOCTYPE html><html lang=en><meta charset=utf-8><title>BMP coverage of %s</title><link rel=stylesheet href=visualization.css type=text/css><h1>BMP coverage of %s</h1><p class=note role=note>This table is not normative.<p><a href='%s.html'>Index</a><p><a href='./#visualization'>Legend</a><table><thead><tr><td><td>") % (name, name, name))
    for i in xrange(256):
        out_file.write("<th>%02d" % i)
    out_file.write("<tr><td><td>")
    for i in xrange(256):
        out_file.write("<th>%02X" % i)
    out_file.write("<tbody>")
    previous = None
    new_row = True
    row_num = -1
    index = indexes[name]
    for code_point in xrange(0x10000):
        if code_point % 256 == 0:
            new_row = True
            row_num += 1
        pointer = bmp[code_point]
        if new_row:
            out_file.write("<tr><th>%02d<th>%02X" % (row_num, row_num))
            new_row = False
        if code_point >= 0xD800 and code_point <= 0xDFFF:
            out_file.write("<td class=surrogate>")
        elif pointer:
            duplicate = code_point in duplicates
            contiguous = previous and previous + 1 == pointer
            out_file.write((u"<td class='%s %s%s%s' aria-label='%s'><dl><dt>U+%04X<dd lang=%s>%s<dd>%d</dl>" % ("contiguous" if contiguous else "discontiguous", classify(code_point), " duplicate" if duplicate else "", check_compatibility(code_point), aria(code_point, contiguous, duplicate), code_point, lang, format_code_point(code_point), pointer)).encode("utf-8"))
        else:
            out_file.write((u"<td class=unmapped aria-label=Unmapped><dl><dt>U+%04X<dd>\uFFFD<dd>\u00A0</dl>" % code_point).encode("utf-8"))
        previous = pointer
    out_file.write("</table>")
    out_file.close()


for (name, row_length, lang) in names_lengths_langs:
    bmp = [None] * 0x10000
    duplicates = set()
    byte_rule = None
    if row_length != 16:
        byte_rule = byte_rules[name]
    format_index(name, row_length, lang, bmp, duplicates, byte_rule)
    format_coverage(name, lang, bmp, duplicates)

bmp = [None] * 0x10000
duplicates = set()
format_index("shift_jis", 188, "ja", bmp, duplicates, byte_rules["shift_jis"])
