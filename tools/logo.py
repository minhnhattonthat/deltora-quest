"""logo.py: English title logo (docs/re/graphics.md G1/G2) on the three logo screens.

The katakana デルトラクエスト above QUEST is removed (background copied down from the rows above it) and 7つの宝石
becomes "The Seven Gems". The build imports gfx/logo_<screen>.png with nitro.import_screens (only changed cells).

    python -X utf8 tools/logo.py    # regenerate gfx/logo_*.png (needs the Windows fonts typeset.py names)
"""
import sys
from pathlib import Path

import numpy as np

import nitro

ROOT = Path(__file__).resolve().parents[1]
GFX = ROOT / "gfx"
SKILL = Path("C:/Users/Nathan/.claude/plugins/cache/retro-translation/translate-retro-game/d6945f695321/skills/translate-retro-game")
# chr: (pal, screens); 465 story, 1620 title, 1625 light (intro). 1623 is not a 1620 screen: it is the bottom title
# screen's map over other tiles (VRAM dump work/qa/title_dump2); rendering it with 1620 only looks plausible.
SCREENS = {465: (464, [466]), 1620: (1621, [1622]), 1625: (1624, [1626])}
KATA = (156, 70, 208, 81)  # x0, y0, x1, y1 (exclusive): the katakana, above QUEST's top outline (row 81)
SUB = (96, 100, 160, 116)  # the 7つの宝石 subtitle, on plain background
SUBTITLE, SUB_Y, SUB_CX = "The Seven Gems", 101, 116  # text, top row, centre x (the castle base starts at x 168)
COPY = (0, 156, 256, 184)  # title screen (1620) only: the (C) lines (G3), on plain background
COPY_LINES = "(C)2006 Deltora Quest Production Committee\nTV Aichi\n(C)2007 NBGI"
OUTLINE = (64, 24, 8)
RAMP = [(160, 24, 16), (208, 64, 16), (240, 128, 32), (248, 200, 64)]  # top -> bottom, like the subtitle's red-gold


def original(files, c, s):
    til, bpp = nitro.tiles(files[c])
    return nitro.render(nitro.palette(files[SCREENS[c][0]]), til, nitro.screen(files[s]), bpp)[:192]


def derived(files, c, s, base, edited):
    """Target for screen s that reuses rows of screen base (1623 = 1622's lower rows moved up): each of its cells
    that shows the same tile as the matching base row takes that base cell's edit."""
    a, b = nitro.screen(files[base]) & 0x3FF, nitro.screen(files[s]) & 0x3FF
    old_base = original(files, c, base)
    out = original(files, c, s).copy()
    for r in range(min(24, len(b))):
        hits, k = max((int((b[r] == a[k]).sum()), k) for k in range(24))
        if hits < 16:
            continue
        for col in np.nonzero(b[r] == a[k])[0]:
            cell = np.s_[k * 8:k * 8 + 8, col * 8:col * 8 + 8]
            if (edited[cell] != old_base[cell]).any():
                out[r * 8:r * 8 + 8, col * 8:col * 8 + 8] = edited[cell]
    return out


def fill(a, box, bottom=False):
    """Background for box: diffused in from the background-coloured pixels on its top, left and right edges (the
    bottom edge is lettering; the Q and the castle touch the sides), plus the grain of the same-sized block above.
    bottom=True: the whole ring around the box is background (text over plain art)."""
    x0, y0, x1, y1 = box
    p = a[y0 - 1:y1 + 1, x0 - 1:x1 + 1].copy()  # one ring around the box
    h, w = p.shape[:2]
    known = np.zeros((h, w), bool)
    known[0], known[:, 0], known[:, -1] = True, True, True
    if bottom:
        known[-1] = True
    else:
        known[-1] = False
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
    if bottom:
        return p[1:, 1:-1].clip(0, 255)
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


def import_pngs(files, c, pngs):
    """-> new files[c] and files[s] for each screen s of chr c, from the target PNGs (same order as SCREENS[c][1])."""
    from PIL import Image
    p, ss = SCREENS[c]
    targets = [np.array(Image.open(png).convert("RGB")) for png in pngs]
    return nitro.import_screens(files[c], files[p], [files[s] for s in ss], targets)


def apply(files):
    for c, (_, ss) in SCREENS.items():
        files[c], new = import_pngs(files, c, [GFX / f"logo_{s}.png" for s in ss])
        for s, b in zip(ss, new):
            files[s] = b


def main():
    from PIL import Image
    import lf2
    import ndspy.rom
    sys.path.insert(0, str(ROOT / "tools"))
    import build
    files = lf2.read(ndspy.rom.NintendoDSRom(build.ROM.read_bytes()).files[build.FILEDATA], [])
    GFX.mkdir(exist_ok=True)
    for c, (_, ss) in SCREENS.items():
        edited = generate(original(files, c, ss[0]), c).round().astype(np.uint8)
        for s in ss:
            out = GFX / f"logo_{s}.png"
            img = edited if s == ss[0] else derived(files, c, s, ss[0], edited)
            Image.fromarray(img).save(out)
            print(out)


if __name__ == "__main__":
    main()
