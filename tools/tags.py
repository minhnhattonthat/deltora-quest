"""tags.py: draw the English speaker name tags (docs/re/graphics.md G5) with fonts/en_font.txt.

Tag n (header word 2 low byte = n * 4, n = 1..45) is FILEDATA 4533 + n: an RGCN of one 64x16 picture, shown as two
32x16 OBJ halves (4bpp, 1D), palette = cyan ramp, 1 brightest .. 15 darkest, 0 transparent.

    python -X utf8 tools/tags.py OUT.png    # contact sheet of every English tag (4x zoom)
"""
import sys
from pathlib import Path

import numpy as np

import fontgen

SMALL = fontgen.ROOT / "fonts/tag_small.txt"
BASE = 4533
W, H, HDR = 64, 16, 0x30
TOP, FILL, SHADOW = 4, 1, 0xB  # cap rows 4-12 as in the Japanese tags; shadow 1 px down-right
NAMES = {
    0x01: "Lief", 0x02: "Barda", 0x03: "Jasmine", 0x04: "Doom", 0x05: "Dain", 0x06: "Jarred", 0x07: "Anna",
    0x08: "Fallow", 0x09: "Prandine", 0x0A: "Sharn", 0x0B: "Crian", 0x0C: "Mother Brightly", 0x0D: "Manus",
    0x0E: "Glock", 0x0F: "Zeean", 0x10: "Fardeep", 0x11: "Old Woman", 0x12: "Tira", 0x13: "Prin",
    0x14: "Kuren", 0x15: "Kin", 0x16: "Fa-Glin", 0x17: "Gla-Thon", 0x18: "Steven", 0x19: "Jack", 0x1A: "Mokito",
    0x1B: "Mikita", 0x1C: "Endon", 0x1D: "???", 0x1E: "Gorl", 0x1F: "Soldeen", 0x20: "Thaegan", 0x21: "Reeah",
    0x22: "Gellick", 0x23: "Ra-Kacharz", 0x24: "Rai", 0x25: "Marie", 0x26: "Ida", 0x27: "Jin", 0x28: "Jod",
    0x29: "Niji", 0x2A: "Dodge", 0x2B: "Ferdinand", 0x2C: "Captain", 0x2D: "Spirit",
}


def decode(rgcn):
    """RGCN bytes -> 16x64 array of palette indices."""
    t = np.frombuffer(rgcn[HDR:HDR + W * H // 2], np.uint8)
    px = np.stack([t & 15, t >> 4], -1).reshape(16, 8, 8)  # 16 tiles of 8x8; tile = half * 8 + row * 4 + col
    img = np.zeros((H, W), np.uint8)
    for k in range(16):
        half, r, c = k // 8, k % 8 // 4, k % 4
        img[r * 8:r * 8 + 8, half * 32 + c * 8:half * 32 + c * 8 + 8] = px[k]
    return img


def encode(img, rgcn):
    """Inverse of decode; keeps rgcn's header."""
    tiles = []
    for k in range(16):
        half, r, c = k // 8, k % 8 // 4, k % 4
        p = img[r * 8:r * 8 + 8, half * 32 + c * 8:half * 32 + c * 8 + 8]
        tiles.append((p[:, 0::2] | (p[:, 1::2] << 4)).tobytes())
    return rgcn[:HDR] + b"".join(tiles) + rgcn[HDR + W * H // 2:]


def line(name, font, space):
    cols = []
    for ch in name:
        cols.append(np.zeros((11, space), bool) if ch == " " else np.array([[c == "#" for c in r] for r in font[ch]], bool))
        cols.append(np.zeros((11, 1), bool))
    return np.concatenate(cols[:-1], 1)


def draw(name, fonts=None):
    """Dialogue font; the small font (as the Japanese tags shrink their longest name) only when that is too wide."""
    big, small = fonts or (fontgen.glyphs(), fontgen.glyphs(SMALL))
    m = line(name, big, fontgen.SPACE)
    if m.shape[1] > W - 1:
        m = line(name, small, 2)
    w = m.shape[1]
    assert w <= W - 1, f"tag {name!r} is {w} px in the small font, {W - 1} fit"
    full = np.zeros((H, W), bool)
    x = (W - 1 - w) // 2
    full[TOP:TOP + 11, x:x + w] = m
    img = np.zeros((H, W), np.uint8)
    shadow = np.roll(np.roll(full, 1, 0), 1, 1) & ~full
    img[shadow] = SHADOW
    img[full] = FILL
    return img


def apply(files):
    fonts = fontgen.glyphs(), fontgen.glyphs(SMALL)
    for n, name in NAMES.items():
        files[BASE + n] = encode(draw(name, fonts), files[BASE + n])


def main():
    from PIL import Image
    ramp = [(0, 0, 0)] + [(0, max(0, 0xE8 - 16 * i), max(0, 0xF8 - 16 * i)) for i in range(15)]
    z = 4
    sheet = Image.new("RGB", (3 * W * z + 2 * 8, 15 * (H * z + 4)), (40, 40, 40))
    for k, (n, name) in enumerate(NAMES.items()):
        rgb = np.array(ramp, np.uint8)[draw(name)]
        im = Image.fromarray(rgb).resize((W * z, H * z), Image.NEAREST)
        sheet.paste(im, ((k % 3) * (W * z + 8), (k // 3) * (H * z + 4)))
    sheet.save(sys.argv[1])
    print(sys.argv[1])


if __name__ == "__main__":
    main()
