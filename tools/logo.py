"""logo.py: English title logo (docs/re/graphics.md G1/G2) on the three logo screens.

The katakana デルトラクエスト above QUEST is removed (background copied down from the rows above it) and 7つの宝石
becomes "The Seven Gems". The build imports gfx/logo_<chr>.png: only 8x8 cells that differ from the original are
re-encoded, each with the one of the screen's 16 palettes that fits it best (index 0 unused, as in the original).

    python -X utf8 tools/logo.py    # regenerate gfx/logo_*.png (needs the Windows fonts typeset.py names)
"""
import sys
from pathlib import Path

import numpy as np

import nitro

ROOT = Path(__file__).resolve().parents[1]
GFX = ROOT / "gfx"
SKILL = Path("C:/Users/Nathan/.claude/plugins/cache/retro-translation/translate-retro-game/d6945f695321/skills/translate-retro-game")
SCREENS = {465: (464, 466), 1620: (1621, 1622), 1625: (1624, 1626)}  # chr: (pal, scr); 465 story, 1620 title
KATA = (156, 70, 208, 81)  # x0, y0, x1, y1 (exclusive): the katakana, above QUEST's top outline (row 81)
SUB = (96, 100, 160, 116)  # the 7つの宝石 subtitle, on plain background
SUBTITLE, SUB_Y, SUB_CX = "The Seven Gems", 101, 116  # text, top row, centre x (the castle base starts at x 168)
COPY = (0, 158, 256, 184)  # title screen (1620) only: the (C) lines (G3), on plain background
COPY_LINES = "(C)2006 Deltora Quest Production Committee\nTV Aichi\n(C)2007 NBGI"
OUTLINE = (64, 24, 8)
RAMP = [(160, 24, 16), (208, 64, 16), (240, 128, 32), (248, 200, 64)]  # top -> bottom, like the subtitle's red-gold


def unpack(files, c):
    p, s = SCREENS[c]
    til, bpp = nitro.tiles(files[c])
    return nitro.palette(files[p]), til, nitro.screen(files[s]), bpp


def original(files, c):
    pal, til, scr, bpp = unpack(files, c)
    return nitro.render(pal, til, scr, bpp)[:192]


def fill(a, box):
    """Background for box: diffused in from the background-coloured pixels on its top, left and right edges (the
    bottom edge is lettering; the Q and the castle touch the sides), plus the grain of the same-sized block above."""
    x0, y0, x1, y1 = box
    p = a[y0 - 1:y1 + 1, x0 - 1:x1 + 1].copy()  # one ring around the box
    h, w = p.shape[:2]
    known = np.zeros((h, w), bool)
    known[0], known[:-1, 0], known[:-1, -1] = True, True, True
    known &= np.abs(p - np.median(p[0], 0)).sum(-1) < 60
    inner = np.zeros((h, w), bool)
    inner[1:-1, 1:-1] = True
    p[inner] = np.median(p[0], 0)
    use = known | inner
    for _ in range(400):
        acc, n = np.zeros_like(p), np.zeros((h, w))
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            k = np.roll(use, (dy, dx), (0, 1))
            acc += np.roll(p, (dy, dx), (0, 1)) * k[..., None]
            n += k
        p[inner] = acc[inner] / n[inner][:, None]
    p = p[:-1]
    above = a[2 * y0 - y1:y0, x0:x1]
    blur = sum(np.roll(np.roll(above, dy, 0), dx, 1) for dy in (-1, 0, 1) for dx in (-1, 0, 1)) / 9
    return (p[1:, 1:-1] + above - blur).clip(0, 255)


def copyright_lines(a):
    import typeset
    x0, y0, x1, y1 = COPY
    region = a[y0:y1, x0:x1]
    ink = region.reshape(-1, 3)[region.sum(-1).argmin()].copy()  # the darkest pixel of the original lines
    region[:] = a[2 * y0 - y1:y0, x0:x1]
    layer = np.array(typeset.text_image(x1 - x0, y1 - y0, COPY_LINES, font_name="sans", size=9, spacing=-2,
                                        fill=(255, 255, 255, 255), pad=0), float)[..., 3:] / 255
    region[:] = region * (1 - layer) + ink * layer


def generate(img, c):
    sys.path.insert(0, str(SKILL / "scripts"))
    import typeset
    a = img.astype(float)
    if c == 1620:
        copyright_lines(a)
    x0, y0, x1, y1 = KATA
    a[y0:y1, x0:x1] = fill(a, KATA)
    x0, y0, x1, y1 = SUB
    a[y0:y1, x0:x1] = img[y1:2 * y1 - y0, x0:x1]
    layer = typeset.text_image(128, 16, SUBTITLE, font_name="georgia-b", size=13, fill=(255, 255, 255, 255))
    m = np.array(layer)[..., 3] >= 128
    ys, xs = np.nonzero(m)
    m = m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h, w = m.shape
    ring = np.zeros((h + 2, w + 2), bool)
    for dy in range(3):
        for dx in range(3):
            ring[dy:dy + h, dx:dx + w] |= m
    x, y = SUB_CX - (w + 2) // 2, SUB_Y
    region = a[y:y + h + 2, x:x + w + 2]
    region[ring] = OUTLINE
    for r in range(h):
        region[r + 1, 1:w + 1][m[r]] = RAMP[min(len(RAMP) - 1, r * len(RAMP) // h)]
    return a


def import_png(files, c, png):
    """Re-encode the cells of FILEDATA c whose pixels differ from the original render."""
    from PIL import Image
    pal, til, scr, bpp = unpack(files, c)
    assert bpp == 4
    new = np.array(Image.open(png).convert("RGB")).astype(int)
    old = nitro.render(pal, til, scr, bpp)[:192].astype(int)
    til, scr = til.copy(), scr.copy()
    ids = (scr & 0x3FF).reshape(-1).tolist()
    free = sorted(set(range(len(til))) - set(ids))
    pals = pal.astype(int).reshape(16, 16, 3)[:, 1:]  # index 0 never used in these screens
    for r in range(24):
        for col in range(32):
            cell = new[r * 8:r * 8 + 8, col * 8:col * 8 + 8]
            if (cell == old[r * 8:r * 8 + 8, col * 8:col * 8 + 8]).all():
                continue
            d = ((cell[None, :, :, None, :] - pals[:, None, None, :, :]) ** 2).sum(-1)  # (16, 8, 8, 15)
            best = int(d.min(-1).sum((1, 2)).argmin())
            e = int(scr[r, col])
            t = e & 0x3FF
            if ids.count(t) > 1:
                t = free.pop(0)  # shared tile: give this cell its own copy
            til[t] = d[best].argmin(-1) + 1
            scr[r, col] = (e & 0x0C00) | t | (best << 12)
    return nitro.with_tiles(files[c], til), nitro.with_screen(files[SCREENS[c][1]], scr)


def apply(files):
    for c in SCREENS:
        files[c], files[SCREENS[c][1]] = import_png(files, c, GFX / f"logo_{c}.png")


def main():
    from PIL import Image
    import lf2
    import ndspy.rom
    sys.path.insert(0, str(ROOT / "tools"))
    import build
    files = lf2.read(ndspy.rom.NintendoDSRom(build.ROM.read_bytes()).files[build.FILEDATA], [])
    GFX.mkdir(exist_ok=True)
    for c in SCREENS:
        out = GFX / f"logo_{c}.png"
        Image.fromarray(generate(original(files, c), c).round().astype(np.uint8)).save(out)
        print(out)


if __name__ == "__main__":
    main()
