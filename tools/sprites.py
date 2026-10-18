"""sprites.py: small sprite labels redrawn in place with the dialogue font (docs/re/graphics.md G16 battle HUD, G17
Save panel). Each spot: cell bank, its RGCN (tiled or linear), the cells to change, and the labels: box (x0, y0, x1,
y1 in the cell picture, exclusive), text, fill and outline palette index, how to clear the old text ("clear" =
transparent, "panel" = each column filled from the rows just above and below the box), cap row, alignment.
"""
import struct

import numpy as np

import banners
import fontgen
import nitro
import tags

SPOTS = {
    # bank: (rgcn, cells, [(box, text, fill, outline, clear, cap row, centred)])
    5591: (5592, [0, 1], [((27, 2, 84, 16), "Time Left", 9, 15, "clear", 4, False),
                          ((86, 2, 170, 16), "Weapon Bonus", 9, 15, "clear", 4, False)]),
    5412: (5411, [0, 1, 2, 3], [((5, 10, 28, 21), "SAVE", 5, 1, "panel", 11, True)]),
}


def draw(img, box, text, fill, outline, clear, cap, centred):
    x0, y0, x1, y1 = box
    if clear == "clear":
        img[y0:y1, x0:x1] = 0
    else:  # nearest of the row above and the row below, per column
        for y in range(y0, y1):
            src = y0 - 1 if y - y0 < y1 - y else y1
            img[y, x0:x1] = img[src, x0:x1]
    m = tags.line(text, fontgen.glyphs(), fontgen.SPACE)
    h, w = m.shape
    full = np.zeros((h + 2, w + 2), bool)
    full[1:-1, 1:-1] = m
    ring = np.zeros_like(full)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            ring |= np.roll(np.roll(full, dy, 0), dx, 1)
    W = img.shape[1]
    x = (W - w - 2) // 2 if centred else x0 + 1
    assert 0 <= x and x + w + 2 <= W and (centred or x + w + 2 <= x1), f"{text!r} does not fit"
    region = img[cap - 1:cap - 1 + h + 2, x:x + w + 2]
    region[ring & ~full] = outline
    region[full] = fill


def apply(files):
    for n, (c, cells, labels) in SPOTS.items():
        r = nitro.parse_recn(files[n])
        lin = bool(struct.unpack_from("<I", nitro.section(files[c], b"RAHC")[1], 0x0C)[0] & 1)
        til, bpp = nitro.tiles(files[c])
        assert bpp == 4
        til = til.copy()
        unit = (32 << r["mapping"]) // 32
        for i in cells:
            objs, W, H = banners.layout(r["cells"][i], r["transfer"][i][0] // 32, unit)
            img = banners.get(til, objs, W, H, lin)
            for spot in labels:
                draw(img, *spot)
            banners.put(til, objs, img, lin)
        files[c] = nitro.with_tiles(files[c], til)


def main():
    """Contact sheet: python -X utf8 tools/sprites.py OUT.png"""
    import sys
    from PIL import Image
    files = {k: nitro.load(k) for k in range(5400, 5600)}
    before = dict(files)
    apply(files)
    rows = []
    for n, (c, cells, _) in SPOTS.items():
        r = nitro.parse_recn(files[n])
        lin = bool(struct.unpack_from("<I", nitro.section(files[c], b"RAHC")[1], 0x0C)[0] & 1)
        pal = nitro.palette(files[next(k for k in range(n - 1, n - 8, -1) if files[k][:4] == b"RLCN")])
        for f in (before, files):
            til, _ = nitro.tiles(f[c])
            ims = []
            for i in cells:
                cell = r["cells"][i]
                objs, W, H = banners.layout(cell, r["transfer"][i][0] // 32, (32 << r["mapping"]) // 32)
                px = banners.get(til, objs, W, H, lin)
                im = pal[(cell["objs"][-1][2] >> 12) * 16 + px]
                im[px == 0] = (255, 0, 255)
                ims.append(np.pad(im, ((0, 2), (0, 2), (0, 0))))
            rows.append(np.concatenate(ims, 1))
    w = max(x.shape[1] for x in rows)
    sheet = np.concatenate([np.pad(x, ((0, 0), (0, w - x.shape[1]), (0, 0))) for x in rows])
    Image.fromarray(sheet).resize((sheet.shape[1] * 3, sheet.shape[0] * 3), Image.NEAREST).save(sys.argv[1])
    print(sys.argv[1])


if __name__ == "__main__":
    main()
