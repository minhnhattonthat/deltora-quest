"""menu.py: English field-menu labels at full width (docs/re/graphics.md G6, decision D8).

The field menu is cell bank FILEDATA 5310 over sheet 5311 (tiled) and its twin 5309 (linear, row-major). Each menu
entry is 3 animation cells of {32x16 label under a 32x32 icon}, whose tiles one VRAM-transfer slice (0x300 bytes)
brings in. The DS has no 64x16 sprite, so each label becomes two 32x16 sprites side by side: the slice grows to 0x400
(label 0x200 + icon 0x200), the sheets are re-packed, and the bank's largest slice is raised to 0x400.
The two top-row entries sit 48 px apart, so their labels are nudged apart (NUDGE).
"""
import math
import struct

import numpy as np

import fontgen
import nitro
import tags

RECN, TILED, LINEAR = 5310, 5311, 5309
LABELS = {0: "Materials", 3: "Equipment", 6: "Key Items", 12: "Cards", 15: "Items"}  # first cell of each entry
NUDGE = {3: -7, 6: 7}  # x shift of the label (px): Equipment left, Key Items right, ~10 px apart
# y shift of a whole entry (icon + label): the wide top-row labels would run under the middle-row icons, so the top
# row goes up 6 px (icons still inside the board) and the middle row down 6 (work/qa/menus3).
LIFT = {3: -6, 6: -6, 0: 6, 12: 6}
SLICE = 0x400


def draw(text, font):
    """64x16 label: fill 1, outline 15 (8-neighbour), caps on rows 2-10 as in the Japanese labels."""
    m = tags.line(text, font, fontgen.SPACE)
    h, w = m.shape
    assert w + 2 <= 64, f"{text!r} is {w + 2} px with its outline"
    full = np.zeros((16, 64), bool)
    x = (64 - w) // 2
    full[2:2 + h, x:x + w] = m[:14]
    ring = np.zeros_like(full)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            ring |= np.roll(np.roll(full, dy, 0), dx, 1)
    return np.where(full, 1, np.where(ring, 15, 0)).astype(np.uint8)


def halves(img):
    """64x16 -> (left, right) 32x16 sprites as tiled bytes (4x2 tiles, 1D)."""
    out = []
    for x0 in (0, 32):
        t = img[:, x0:x0 + 32].reshape(2, 8, 4, 8).transpose(0, 2, 1, 3).reshape(8, 8, 8)
        out.append((t[..., 0::2] | (t[..., 1::2] << 4)).astype(np.uint8).tobytes())
    return out


def row_major(img):
    return (img[:, 0::2] | (img[:, 1::2] << 4)).astype(np.uint8).tobytes()


def shift_y(a0, dy):
    """OAM attr 0 with its signed 8-bit y moved by dy."""
    y = (a0 & 0xFF) - (256 if a0 & 0x80 else 0) + dy
    assert -128 <= y < 128
    return (a0 & ~0xFF) | (y & 0xFF)


def radius(objs):
    """Cell attr low bits: bounding radius / 4, as the originals have (9 for label + icon, 6 for an icon)."""
    far = 0
    for a0, a1, _ in objs:
        w, h = {(1, 2): (32, 16), (0, 2): (32, 32)}[(a0 >> 14, a1 >> 14)]
        y, x = (a0 & 0xFF) - (256 if a0 & 0x80 else 0), (a1 & 0x1FF) - (512 if a1 & 0x100 else 0)
        far = max(far, max(math.hypot(px, py) for px in (x, x + w) for py in (y, y + h)))
    return math.ceil(far / 4)


def apply(files):
    r = nitro.parse_recn(files[RECN])
    tiled = nitro.section(files[TILED], b"RAHC")[1][0x18:]
    lin = nitro.section(files[LINEAR], b"RAHC")[1][0x18:]
    font = fontgen.glyphs()
    new_t, new_l, transfer = b"", b"", []
    entry = None
    for i, (cell, (src, size)) in enumerate(zip(r["cells"], r["transfer"])):
        entry = i if i in LABELS else entry
        if len(cell["objs"]) == 1:  # icon only (the back button): unchanged
            transfer.append((len(new_t), size))
            new_t, new_l = new_t + tiled[src:src + size], new_l + lin[src:src + size]
            continue
        (la0, la1, la2), icon = cell["objs"]
        assert size == 0x300 and (la0 >> 14, la1 >> 14, la2 & 0x3FF) == (1, 2, 0) and icon[2] & 0x3FF == 2
        img = draw(LABELS[entry], font)
        left, right = halves(img)
        x = -32 + NUDGE.get(entry, 0)
        dy = LIFT.get(entry, 0)
        la0, i0 = shift_y(la0, dy), shift_y(icon[0], dy)
        objs = [(la0, (la1 & ~0x1FF) | (x & 0x1FF), la2 & ~0x3FF),
                (la0, (la1 & ~0x1FF) | ((x + 32) & 0x1FF), (la2 & ~0x3FF) | 2),
                (i0, icon[1], (icon[2] & ~0x3FF) | 4)]
        r["cells"][i] = {"attr": (cell["attr"] & ~0x3F) | radius(objs), "objs": objs}
        transfer.append((len(new_t), SLICE))
        new_t += left + right + tiled[src + 0x100:src + 0x300]
        new_l += row_major(img[:, :32]) + row_major(img[:, 32:]) + lin[src + 0x100:src + 0x300]
    r["transfer"], r["max_transfer"] = transfer, SLICE
    files[RECN] = nitro.build_recn(r)
    files[TILED] = nitro.with_data(files[TILED], new_t)
    files[LINEAR] = nitro.with_data(files[LINEAR], new_l)


def main():
    """Contact sheet of the re-packed cells: python -X utf8 tools/menu.py OUT.png"""
    import sys
    from PIL import Image
    sys.path.insert(0, str(nitro.ROOT / "tools/debug"))
    import objsurvey
    files = {n: nitro.load(n) for n in (5307, RECN, TILED, LINEAR)}
    apply(files)
    pal = nitro.palette(files[5307])
    rows = []
    for n, lin in ((TILED, False), (LINEAR, True)):
        til, _ = nitro.tiles(files[n])
        ims = [im for _, im in objsurvey.cells(files[RECN], til, pal, lin)]
        rows.append(np.concatenate([np.pad(im, ((0, 48 - im.shape[0]), (0, 72 - im.shape[1]), (0, 0))) for im in ims], 1))
    im = np.concatenate(rows)
    Image.fromarray(im).resize((im.shape[1] * 2, im.shape[0] * 2), Image.NEAREST).save(sys.argv[1])
    print(sys.argv[1])


if __name__ == "__main__":
    main()
