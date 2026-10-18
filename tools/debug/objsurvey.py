"""objsurvey.py: render every sprite cell in FILEDATA (RECN cell banks with the RGCN after them and the RLCN before)
into packed contact sheets, to find text drawn as sprites without reaching each screen (docs/re/graphics.md).

    python -X utf8 tools/debug/objsurvey.py [--out work/qa/objsurvey]
RECN (KBEC): u16 cells, u16 attr (bit 0: 16-byte entries), u32 entry offset, u32 mapping (tile unit 32 << n bytes),
u32 VRAM-transfer table offset (0 = none; else {u32 max size, u32 table offset}, then per cell {u32 src, u32 size}:
the cell's tiles are RGCN data[src:src+size], indices relative to it). Entries {u16 objs, u16 attr, u32 obj offset};
objs are 3 x u16 OAM attributes, x/y relative to the cell centre. Identical renders are drawn once.
"""
import argparse
import hashlib
import struct
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import nitro  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SIZES = {0: [(8, 8), (16, 16), (32, 32), (64, 64)], 1: [(16, 8), (32, 8), (32, 16), (64, 32)],
         2: [(8, 16), (8, 32), (16, 32), (32, 64)]}


def cells(recn, til, pal):
    off = struct.unpack_from("<H", recn, 0x0C)[0]
    s = recn[off + 8:]
    n, attr, coff, mapping, vt = struct.unpack_from("<HHIII", s, 0)
    esz = 16 if attr & 1 else 8
    unit = (32 << mapping) // 32  # tiles per index step
    src = [0] * n
    if vt:
        tab = vt + struct.unpack_from("<I", s, vt + 4)[0]
        src = [struct.unpack_from("<I", s, tab + i * 8)[0] // 32 for i in range(n)]
    oam0 = coff + n * esz
    for i in range(n):
        nobj, _, ooff = struct.unpack_from("<HHI", s, coff + i * esz)
        objs = []
        for k in range(nobj):
            a0, a1, a2 = struct.unpack_from("<HHH", s, oam0 + ooff + k * 6)
            if a0 >> 14 == 3:
                continue
            w, h = SIZES[a0 >> 14][a1 >> 14]
            y, x = (a0 & 0xFF) - (256 if a0 & 0x80 else 0), (a1 & 0x1FF) - (512 if a1 & 0x100 else 0)
            objs.append((x, y, w, h, src[i] + (a2 & 0x3FF) * unit, a2 >> 12, a1 >> 12 & 1, a1 >> 13 & 1))
        if not objs:
            continue
        x0, y0 = min(o[0] for o in objs), min(o[1] for o in objs)
        x1, y1 = max(o[0] + o[2] for o in objs), max(o[1] + o[3] for o in objs)
        if x1 - x0 > 256 or y1 - y0 > 256:
            continue
        img = np.zeros((y1 - y0, x1 - x0, 3), np.uint8)
        img[:] = (255, 0, 255)
        for x, y, w, h, t, p, hf, vf in objs:
            k = np.arange(w * h // 64) + t
            if k[-1] >= len(til):
                continue
            px = til[k].reshape(h // 8, w // 8, 8, 8).transpose(0, 2, 1, 3).reshape(h, w)
            if hf:
                px = px[:, ::-1]
            if vf:
                px = px[::-1]
            rgb = pal[(p * 16 + px) % len(pal)]
            m = px != 0
            img[y - y0:y - y0 + h, x - x0:x - x0 + w][m] = rgb[m]
        yield i, img


def main():
    from PIL import Image, ImageDraw
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "work/qa/objsurvey"))
    ap.add_argument("--width", type=int, default=1600)
    ap.add_argument("--height", type=int, default=1000)
    a = ap.parse_args()
    d = ROOT / "work/fs/lf2"
    magic = {int(p.stem): p.read_bytes()[:4] for p in d.iterdir()}
    seen, items = set(), []
    for n in sorted(magic):
        if magic[n] != b"RECN":
            continue
        c = n + 1 if magic.get(n + 1) == b"RGCN" else next((k for k in range(n - 1, n - 6, -1) if magic.get(k) == b"RGCN"), None)
        p = next((k for k in range(n - 1, n - 8, -1) if magic.get(k) == b"RLCN"), None)
        if c is None or p is None:
            continue
        try:
            til, bpp = nitro.tiles(nitro.load(c))
            if bpp != 4:
                continue
            pal = nitro.palette(nitro.load(p))
            for i, img in cells(nitro.load(n), til, pal):
                h = hashlib.sha1(img.tobytes()).digest()
                if h not in seen and (img != (255, 0, 255)).any():
                    seen.add(h)
                    items.append((f"{n}:{i}", img))
        except Exception as e:  # noqa: BLE001  survey: list what doesn't decode
            print(f"skip {n}: {e}")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    sheets, x, y, rowh, k = [], 0, 0, 0, 0
    sheet = Image.new("RGB", (a.width, a.height), (40, 40, 40))
    dr = ImageDraw.Draw(sheet)
    for lab, img in items:
        h, w = img.shape[:2]
        if x + max(w, 60) > a.width:
            x, y, rowh = 0, y + rowh + 12, 0
        if y + h + 12 > a.height:
            sheets.append(sheet)
            sheet = Image.new("RGB", (a.width, a.height), (40, 40, 40))
            dr = ImageDraw.Draw(sheet)
            x = y = rowh = 0
        dr.text((x, y), lab, fill=(255, 255, 0))
        sheet.paste(Image.fromarray(img), (x, y + 10))
        x += max(w, 60) + 4
        rowh = max(rowh, h)
    sheets.append(sheet)
    for i, s in enumerate(sheets):
        s.save(out / f"sheet_{i:02}.png")
    print(len(items), "unique cells,", len(sheets), "sheets in", out)


if __name__ == "__main__":
    main()
