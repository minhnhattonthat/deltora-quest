"""cards.py: English chapter and area title cards (docs/re/graphics.md G8/G9): white text with a grey glow on black.

Each card is a BG screen (RCSN) over its own RGCN. generate() blanks the screen to its background colour and draws
a small top line and a large main line where the Japanese had them; the build imports gfx/card_<screen>.png with
nitro.import_screens, passing every RCSN between the RGCN and the next one too (a screen that doesn't really use
these tiles is left as it is and only keeps its tiles from being reused).

    python -X utf8 tools/cards.py    # regenerate gfx/card_*.png (needs the Windows fonts typeset.py names)
"""
import sys
from pathlib import Path

import numpy as np

import nitro

ROOT = Path(__file__).resolve().parents[1]
GFX = ROOT / "gfx"
SKILL = Path("C:/Users/Nathan/.claude/plugins/cache/retro-translation/translate-retro-game/d6945f695321/skills/translate-retro-game")
# screen: (chr, palette, top line, main line); names per glossary.md
CARDS = {
    1694: (1693, 1689, "Chapter 1", "The Forests of Silence"),
    1701: (1700, 1696, "Chapter 2", "The Lake of Tears"),
    1708: (1707, 1703, "Chapter 3", "The City of the Rats"),
    1715: (1714, 1710, "Chapter 4", "The Shifting Sands"),
    1722: (1721, 1717, "Chapter 5", "Dread Mountain"),
    1729: (1728, 1724, "Chapter 6", "The Maze of the Beast"),
    1736: (1735, 1731, "Chapter 7", "The Valley of the Lost"),
    1743: (1742, 1738, "Final Chapter", "Return to Del"),
    1750: (1749, 1745, "The Cosy", "Camp"),
    1757: (1756, 1752, "", "Tom's Shop"),
    1764: (1763, 1759, "Jasmine's", "Mixing Room"),
    1771: (1770, 1766, "Special Stage", "Mokito's Mansion"),
    1778: (1777, 1773, "Jack's", "Grand Farm"),
    1785: (1784, 1780, "Extra Stage", "The Tower of Dreams"),
    1792: (1791, 1787, "The Secret", "Audio Room"),
}
# One-line outlined labels redrawn in the dialogue font: screen: (chr, palette, text, box of the Japanese line,
# letter colour "red"/"bright", centred). G10 game over, G7 item menu header.
LABELS = {
    425: (424, 423, "Lief's party has fallen...", (6, 12, 154, 30), "red", False),
    542: (541, 540, "Items for Use in the Field", (56, 8, 204, 21), "bright", True),
    1675: (1674, 1673, "Deltora Card Trade", (56, 7, 206, 21), "bright", False),  # G11, wireless card trade
    1678: (1677, 1676, "Trading Deltora Cards...", (56, 7, 206, 21), "bright", False),
    # G13, store-demo screens (script 1927 loads 376's tiles, so maybe reachable)
    374: (373, 372, "Tap the screen and tag the next player!", (4, 97, 252, 120), "red", True),
    376: (375, 372, "Deltora Quest is coming this year.\nLook forward to the rest of it...", (10, 134, 246, 181),
          "bright", True),
}
# Japanese removed, nothing drawn: screen: (chr, palette, box). G12: the Japanese translation under Emily Rodda's
# handwritten English letter (the English original stays).
ERASE = {357: (355, 356, (28, 113, 228, 183))}
TOP_Y, MAIN_Y = 59, 110  # line centres, as in the Japanese cards
TOP_SIZE, MAIN_SIZE, WIDTH = 15, 22, 240
FILL, GLOW = np.array([248, 248, 248]), np.array([120, 120, 120])


def neighbours(files_magic, c):
    """RCSN files after chr c up to the next RGCN: the screens that can be drawn over it (the card among them)."""
    out, k = [], c + 1
    while files_magic(k) not in (b"RGCN", None):
        if files_magic(k) == b"RCSN":
            out.append(k)
        k += 1
    return out


def original(files, s):
    c, p = CARDS[s][:2]
    til, bpp = nitro.tiles(files[c])
    return nitro.render(nitro.palette(files[p]), til, nitro.screen(files[s]), bpp)[:192]


def text_alpha(text, size):
    import typeset
    from PIL import Image
    if not text:
        return np.zeros((1, 1))
    while True:
        img = typeset.text_image(256, 48, text, font_name="sans", size=size, fill=(255, 255, 255, 255), pad=0)
        a = np.array(img)[..., 3] / 255
        ys, xs = np.nonzero(a > 0.05)
        if xs.max() - xs.min() + 1 <= WIDTH or size <= 10:
            return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        size -= 1


def put(img, a, cy):
    h, w = a.shape
    pad = 2
    glow = np.zeros((h + 2 * pad, w + 2 * pad))
    for dy in range(-pad, pad + 1):
        for dx in range(-pad, pad + 1):
            if dy * dy + dx * dx <= pad * pad + 1:
                glow[pad + dy:pad + dy + h, pad + dx:pad + dx + w] = np.maximum(
                    glow[pad + dy:pad + dy + h, pad + dx:pad + dx + w], a * (0.9 if dy or dx else 1))
    y0, x0 = cy - (h + 2 * pad) // 2, 128 - (w + 2 * pad) // 2
    region = img[y0:y0 + h + 2 * pad, x0:x0 + w + 2 * pad]
    region[:] = region * (1 - glow[..., None]) + GLOW * glow[..., None]
    core = np.pad(a, pad)[..., None]
    region[:] = region * (1 - core) + FILL * core


def generate(img, top, main):
    sys.path.insert(0, str(SKILL / "scripts"))
    flat = img.reshape(-1, 3)
    vals, counts = np.unique(flat, axis=0, return_counts=True)
    out = np.empty(img.shape, float)
    out[:] = vals[counts.argmax()]  # the card's background colour
    put(out, text_alpha(top, TOP_SIZE), TOP_Y)
    put(out, text_alpha(main, MAIN_SIZE), MAIN_Y)
    return out.round().astype(np.uint8)


def relabel(img, text, box, colour, centre):
    """Replace an outlined label inside box (plain background around it) with text in the dialogue font; "\\n"
    stacks lines. colour: "red" = the letters are the reddest pixels, "bright" = the brightest; outline = the
    darkest pixel."""
    import fontgen
    import logo
    import tags
    x0, y0, x1, y1 = box
    reg = img[y0:y1, x0:x1].astype(int)
    if colour == "red":
        fill = np.median(reg[reg[..., 0] - reg[..., 1:].max(-1) > 80], 0)
    else:
        fill = reg.reshape(-1, 3)[reg.sum(-1).argmax()]
    ink = reg.reshape(-1, 3)[reg.sum(-1).argmin()]
    a = img.astype(float)
    a[y0:y1, x0:x1] = logo.fill(a, box, bottom=True)
    lines = text.split("\n")
    pitch = 13  # 11 glyph rows + outline
    y = y0 + (y1 - y0 - pitch * len(lines)) // 2 + 1
    for line in lines:
        m = tags.line(line, fontgen.glyphs(), fontgen.SPACE)
        h, w = m.shape
        full = np.zeros((h + 2, w + 2), bool)
        full[1:-1, 1:-1] = m
        ring = np.zeros_like(full)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                ring |= np.roll(np.roll(full, dy, 0), dx, 1)
        assert w + 2 <= x1 - x0, f"{line!r}: {w + 2} px, box is {x1 - x0}"
        x = x0 + (x1 - x0 - w - 2) // 2 if centre else x0 + 2
        region = a[y:y + h + 2, x:x + w + 2]
        region[ring & ~full] = ink
        region[full] = fill
        y += pitch
    return a.round().astype(np.uint8)


def erase(img, box):
    """Dark lettering inside box -> the paper around it. Ink = 30 darker than its 9x9 neighbourhood (thin sharp
    strokes; the vignette and the paper's mottling are smooth), plus a 2 px halo for the anti-aliased edges; filled by
    diffusion from the pixels left."""
    x0, y0, x1, y1 = box
    a = img.astype(float)
    lum = a.mean(-1)
    local = sum(np.roll(np.roll(lum, dy, 0), dx, 1) for dy in range(-4, 5) for dx in range(-4, 5)) / 81
    y0, x0, y1, x1 = y0 - 1, x0 - 1, y1 + 1, x1 + 1  # a known 1 px border, so the rolls below never wrap
    reg = a[y0:y1, x0:x1]
    m = (lum < local - 30)[y0:y1, x0:x1]
    for _ in range(2):
        g = m.copy()
        g[1:] |= m[:-1]
        g[:-1] |= m[1:]
        g[:, 1:] |= m[:, :-1]
        g[:, :-1] |= m[:, 1:]
        m = g
    m[0], m[-1], m[:, 0], m[:, -1] = False, False, False, False
    known = ~m
    cur = reg.copy()
    for _ in range(200):
        acc, n = np.zeros_like(cur), np.zeros(m.shape)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            k = np.roll(known, (dy, dx), (0, 1))
            acc += np.roll(cur, (dy, dx), (0, 1)) * k[..., None]
            n += k
        grow = ~known & (n > 0)
        cur[grow] = acc[grow] / n[grow][:, None]
        known = known | grow
    a[y0:y1, x0:x1] = cur
    return a.round().astype(np.uint8)


def original_label(files, s):
    c, p = (LABELS.get(s) or ERASE[s])[:2]
    til, bpp = nitro.tiles(files[c])
    return nitro.render(nitro.palette(files[p]), til, nitro.screen(files[s]), bpp)[:192]


def apply(files):
    from PIL import Image
    magic = lambda k: files[k][:4] if 0 <= k < len(files) else None  # noqa: E731
    for s, (c, p, *_) in list(CARDS.items()) + list(LABELS.items()) + list(ERASE.items()):
        screens = neighbours(magic, c)
        targets = [np.array(Image.open(GFX / f"card_{s}.png").convert("RGB")) if k == s else
                   nitro.render(nitro.palette(files[p]), nitro.tiles(files[c])[0], nitro.screen(files[k]), 4)
                   for k in screens]
        files[c], new = nitro.import_screens(files[c], files[p], [files[k] for k in screens], targets)
        for k, b in zip(screens, new):
            files[k] = b


def main():
    from PIL import Image
    import lf2
    import ndspy.rom
    import build
    files = lf2.read(ndspy.rom.NintendoDSRom(build.ROM.read_bytes()).files[build.FILEDATA], [])
    GFX.mkdir(exist_ok=True)
    for s, (_, _, top, main_) in CARDS.items():
        out = GFX / f"card_{s}.png"
        Image.fromarray(generate(original(files, s), top, main_)).save(out)
        print(out)
    for s, (_, _, text, box, colour, centre) in LABELS.items():
        out = GFX / f"card_{s}.png"
        Image.fromarray(relabel(original_label(files, s), text, box, colour, centre)).save(out)
        print(out)
    for s, (_, _, box) in ERASE.items():
        out = GFX / f"card_{s}.png"
        Image.fromarray(erase(original_label(files, s), box)).save(out)
        print(out)


if __name__ == "__main__":
    main()
