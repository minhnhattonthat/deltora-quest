"""banners.py: English battle move-name banners (docs/re/graphics.md G15, names per decision D9).

Each banner is a cell bank with 4 cells (colour frames) of 64x32 / 32x32 sprites over one tiled RGCN. The English is
drawn as a bold italic mask; every frame keeps its own colours (the frames flash by changing them): the letters take
the fill index the Japanese letters used most in that frame, the 1 px ring that frame's outline index.

    python -X utf8 tools/banners.py OUT.png    # contact sheet of the redrawn frames
"""
import struct
import sys
from pathlib import Path

import numpy as np

import nitro

SKILL = Path("C:/Users/Nathan/.claude/plugins/cache/retro-translation/translate-retro-game/d6945f695321/skills/translate-retro-game")
# cell bank: (main line, small line above it or "")
BANNERS = {
    5505: ("First Slash", ""), 5509: ("Flash Slash", ""), 5512: ("Spinning Cut", ""),
    5526: ("Help Me, Kree!", ""), 5530: ("Forest Dance", ""), 5533: ("Lend a Hand, Kree!", ""),
    5546: ("Blaze", "Palace Guard Style"), 5549: ("Thunderclap", "Palace Guard Style"),
}
SIZES = {0: [(8, 8), (16, 16), (32, 32), (64, 64)], 1: [(16, 8), (32, 8), (32, 16), (64, 32)],
         2: [(8, 16), (8, 32), (16, 32), (32, 64)]}


def layout(cell, src_tiles, unit):
    """-> [(x, y, w, h, first tile)] relative to the cell's top-left, and the cell size."""
    objs = []
    for a0, a1, a2 in cell["objs"]:
        w, h = SIZES[a0 >> 14][a1 >> 14]
        y, x = (a0 & 0xFF) - (256 if a0 & 0x80 else 0), (a1 & 0x1FF) - (512 if a1 & 0x100 else 0)
        objs.append([x, y, w, h, src_tiles + (a2 & 0x3FF) * unit])
    x0, y0 = min(o[0] for o in objs), min(o[1] for o in objs)
    for o in objs:
        o[0] -= x0
        o[1] -= y0
    return objs, max(o[0] + o[2] for o in objs), max(o[1] + o[3] for o in objs)


def get(til, objs, W, H, linear=False):
    """Cell picture (palette indices) from tiles; linear = the RGCN stores each sprite's pixels row-major."""
    img = np.zeros((H, W), np.uint8)
    for x, y, w, h, t in objs:
        if linear:
            img[y:y + h, x:x + w] = til.reshape(-1)[t * 64:t * 64 + w * h].reshape(h, w)
        else:
            img[y:y + h, x:x + w] = til[t:t + w * h // 64].reshape(h // 8, w // 8, 8, 8).transpose(0, 2, 1, 3).reshape(h, w)
    return img


def put(til, objs, img, linear=False):
    for x, y, w, h, t in objs:
        if linear:
            til.reshape(-1)[t * 64:t * 64 + w * h] = img[y:y + h, x:x + w].reshape(-1)
        else:
            til[t:t + w * h // 64] = img[y:y + h, x:x + w].reshape(h // 8, 8, w // 8, 8).transpose(0, 2, 1, 3).reshape(-1, 8, 8)


def mask(text, size, width, height, italic=0.22):
    """Binary bold italic text mask, shrunk until it fits width x height."""
    sys.path.insert(0, str(SKILL / "scripts"))
    import typeset
    from PIL import Image
    while True:
        img = typeset.text_image(400, 64, text, font_name="sans-b", size=size, fill=(255, 255, 255, 255), pad=0)
        img = img.transform(img.size, Image.AFFINE, (1, italic, -italic * 32, 0, 1, 0), Image.BICUBIC)
        m = np.array(img)[..., 3] >= 128
        ys, xs = np.nonzero(m)
        m = m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        if (m.shape[1] <= width and m.shape[0] <= height) or size <= 8:
            return m
        size -= 1


def ring(m):
    r = np.zeros((m.shape[0] + 2, m.shape[1] + 2), bool)
    for dy in range(3):
        for dx in range(3):
            r[dy:dy + m.shape[0], dx:dx + m.shape[1]] |= m
    return r


def recolour(orig, lines):
    """New frame from the Japanese frame orig (palette indices): lines = [(mask, top row)]."""
    edge = orig != 0
    inner = edge.copy()
    inner[1:-1, 1:-1] &= edge[:-2, 1:-1] & edge[2:, 1:-1] & edge[1:-1, :-2] & edge[1:-1, 2:]
    outline = np.bincount(orig[edge & ~inner], minlength=16)[1:].argmax() + 1
    v = orig[inner & (orig != outline)]
    fill = np.bincount(v, minlength=16).argmax()  # one main colour per frame; the rest is edge shading
    out = np.zeros_like(orig)
    for m, top in lines:
        h, w = m.shape
        out[top:top + h + 2, 1:w + 3][ring(m)] = outline
        out[top + 1:top + 1 + h, 2:w + 2][m] = fill
    return out


def pixel_mask(text):
    """The dialogue pixel font (for the small line, too small for a TrueType face)."""
    import fontgen
    import tags
    return tags.line(text, fontgen.glyphs(), fontgen.SPACE)


def apply(files):
    for n, (main, small) in BANNERS.items():
        r = nitro.parse_recn(files[n])
        assert files[n + 1][:4] == b"RGCN"
        til, bpp = nitro.tiles(files[n + 1])
        assert bpp == 4 and not struct.unpack_from("<I", nitro.section(files[n + 1], b"RAHC")[1], 0x0C)[0] & 1
        til = til.copy()
        unit = (32 << r["mapping"]) // 32
        for cell, (src, _) in zip(r["cells"], r["transfer"]):
            objs, W, H = layout(cell, src // 32, unit)
            orig = get(til, objs, W, H)
            if small:
                s = pixel_mask(small)
                m = mask(main, 22, W - 4, H - s.shape[0] - 5)
                lines = [(s, 0), (m, s.shape[0] + 2)]
            else:
                m = mask(main, 22, W - 4, H - 6)
                lines = [(m, (H - m.shape[0] - 2) // 2)]
            put(til, objs, recolour(orig, lines))
        files[n + 1] = nitro.with_tiles(files[n + 1], til)


def main():
    from PIL import Image
    import lf2
    import ndspy.rom
    sys.path.insert(0, str(nitro.ROOT / "tools"))
    import build
    files = lf2.read(ndspy.rom.NintendoDSRom(build.ROM.read_bytes()).files[build.FILEDATA], [])
    apply(files)
    rows = []
    for n in BANNERS:
        r = nitro.parse_recn(files[n])
        til, _ = nitro.tiles(files[n + 1])
        pal = nitro.palette(files[next(k for k in range(n - 1, n - 8, -1) if files[k][:4] == b"RLCN")])
        imgs = []
        for cell, (src, _) in zip(r["cells"], r["transfer"]):
            objs, W, H = layout(cell, src // 32, (32 << r["mapping"]) // 32)
            p = (cell["objs"][0][2] >> 12) * 16
            im = pal[(p + get(til, objs, W, H)) % len(pal)]
            im[get(til, objs, W, H) == 0] = (60, 60, 60)
            imgs.append(np.pad(im, ((0, 2), (0, 230 - W), (0, 0))))
        rows.append(np.concatenate(imgs, 1))
    sheet = np.concatenate([np.pad(r, ((0, 0), (0, max(x.shape[1] for x in rows) - r.shape[1]), (0, 0))) for r in rows])
    Image.fromarray(sheet).resize((sheet.shape[1] * 2, sheet.shape[0] * 2), Image.NEAREST).save(sys.argv[1])
    print(sys.argv[1])


if __name__ == "__main__":
    main()
