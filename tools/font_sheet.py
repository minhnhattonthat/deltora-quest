"""font_sheet.py: labelled, zoomed sheet of font cells for reading glyphs by eye.

    python -X utf8 tools/font_sheet.py OUT.png --from 0x140 --count 64 [--zoom 5] [--tbl tbl/jp.tbl]
Each cell shows the glyph, its hex code and (with --tbl) the current table entry, so a wrong entry stands out.
"""
import argparse

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import build
import font
import lf2
import ndspy.rom

PALETTE = {0: (40, 40, 60), 1: (255, 255, 255), 2: (220, 220, 220), 3: (180, 180, 180), 4: (140, 140, 140),
           0xE: (90, 0, 0), 0xF: (0, 0, 0)}


def load_tbl(path):
    t = {}
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            t[int.from_bytes(bytes.fromhex(k), "little")] = v  # keys are the LE bytes
    return t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--from", dest="lo", type=lambda s: int(s, 0), default=0x140)
    ap.add_argument("--count", type=int, default=64)
    ap.add_argument("--zoom", type=int, default=5)
    ap.add_argument("--cols", type=int, default=8)
    ap.add_argument("--tbl")
    a = ap.parse_args()
    data = lf2.read(ndspy.rom.NintendoDSRom(build.ROM.read_bytes()).files[build.FILEDATA])[font.FONT_FILE]
    tbl = load_tbl(a.tbl) if a.tbl else {}
    z, cw, ch = a.zoom, 16 * a.zoom + 8, 16 * a.zoom + 34
    rows = -(-a.count // a.cols)
    im = Image.new("RGB", (a.cols * cw, rows * ch), (255, 255, 230))
    dr = ImageDraw.Draw(im)
    lab = ImageFont.truetype("C:/Windows/Fonts/msgothic.ttc", 16)
    for i in range(a.count):
        code = a.lo + i
        if code >= font.NGLYPHS:
            break
        g = font.glyph(data, code)
        rgb = np.array([[PALETTE.get(int(v), (255, 0, 255)) for v in row] for row in g], np.uint8)
        cell = Image.fromarray(rgb).resize((16 * z, 16 * z), Image.NEAREST)
        x, y = (i % a.cols) * cw + 4, (i // a.cols) * ch + 2
        im.paste(cell, (x, y))
        dr.text((x, y + 16 * z + 2), f"{code:03X} {tbl.get(code, '')}", fill=(0, 0, 160), font=lab)
    im.save(a.out)
    print(a.out)


if __name__ == "__main__":
    main()
