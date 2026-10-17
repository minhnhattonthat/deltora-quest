"""font_ocr.py: guess the kanji behind each font cell by template matching against Windows Japanese fonts.

    python -X utf8 tools/font_ocr.py FONT.rgcn OUT.tsv [--from 0x140] [--to 0x500]
Writes code<TAB>best<TAB>score<TAB>top5. Scores are normalised correlations; review low ones by eye
(tools/font_sheet.py) and fix them in tbl/jp.tbl, which is the source of truth.
"""
import argparse

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import font

FONTS = ["C:/Windows/Fonts/msgothic.ttc", "C:/Windows/Fonts/YuGothM.ttc", "C:/Windows/Fonts/YuGothB.ttc"]
SIZES = (10, 11, 12, 13)


def kanji():
    out = []
    for hi in range(0x88, 0xEB):
        for lo in list(range(0x40, 0x7F)) + list(range(0x80, 0xFD)):
            try:
                c = bytes([hi, lo]).decode("cp932")
            except UnicodeDecodeError:
                continue
            if "\u4e00" <= c <= "\u9fff" or c in "々〆":
                out.append(c)
    return sorted(set(out))


def norm(a):
    a = a - a.mean()
    n = np.linalg.norm(a)
    return a / n if n else a


def crop_box(a, thr=0.15):
    ys, xs = np.nonzero(a > thr)
    if not len(ys):
        return a
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def fit(a, n=16):
    """Bounding box scaled to n x n (nearest is fine: both sides get the same treatment)."""
    a = crop_box(a)
    im = Image.fromarray((a * 255).astype(np.uint8)).resize((n, n), Image.BILINEAR)
    return np.asarray(im, np.float32) / 255


def render(ch, path, size):
    f = ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.BASIC)
    im = Image.new("L", (24, 24))
    ImageDraw.Draw(im).text((2, 2), ch, fill=255, font=f)
    return np.asarray(im, np.float32) / 255


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rgcn")
    ap.add_argument("out")
    ap.add_argument("--from", dest="lo", type=lambda s: int(s, 0), default=0x140)
    ap.add_argument("--to", dest="hi", type=lambda s: int(s, 0), default=font.NGLYPHS)
    a = ap.parse_args()
    cands = kanji()
    refs = []
    for c in cands:
        for p in FONTS:
            for s in SIZES:
                refs.append((c, norm(fit(render(c, p, s))).ravel()))
    chars = [c for c, _ in refs]
    mat = np.stack([v for _, v in refs])
    data = open(a.rgcn, "rb").read()
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        for code in range(a.lo, a.hi):
            g = font.fill(font.glyph(data, code))
            if g.max() == 0:
                continue
            sc = mat @ norm(fit(g)).ravel()
            best = {}
            for i in np.argsort(-sc)[:60]:
                best.setdefault(chars[i], float(sc[i]))
            top = sorted(best.items(), key=lambda kv: -kv[1])[:5]
            f.write(f"{code:04X}\t{top[0][0]}\t{top[0][1]:.3f}\t{' '.join(c + format(s, '.2f') for c, s in top)}\n")


if __name__ == "__main__":
    main()
