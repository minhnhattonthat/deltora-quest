"""objcell.py: where a sprite's pixels come from. For OAM entries of a dump (tools/debug/dump_at.lua), take the
cell's tile bytes from OBJ VRAM, list every FILEDATA file + offset holding that exact run, and render the cells.

    python -X utf8 tools/debug/objcell.py work/qa/dump_menu/dump_000060 1 3 5 [--engine A] [--png out.png]
4bpp, 1D mapping only (what this game uses). Offsets are byte offsets in work/fs/lf2/NNNN.bin (tools/unpack.py).
The LABELS lists in tools/tags.py are built from this output.
"""
import argparse
import struct
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SIZES = {0: [(8, 8), (16, 16), (32, 32), (64, 64)], 1: [(16, 8), (32, 8), (32, 16), (64, 32)],
         2: [(8, 16), (8, 32), (16, 32), (32, 64)]}


def sprites(prefix, eng):
    oam = Path(prefix + ".oam.bin").read_bytes()[0 if eng == "A" else 0x400:][:0x400]
    dispcnt = struct.unpack_from("<I", Path(prefix + ".io.bin").read_bytes(), 0 if eng == "A" else 0x60)[0]
    gran = 32 << ((dispcnt >> 20) & 3)
    for i in range(128):
        a0, a1, a2 = struct.unpack_from("<HHH", oam, i * 8)
        if (a0 >> 8) & 3 == 2 or a0 >> 14 == 3:
            continue
        w, h = SIZES[a0 >> 14][a1 >> 14]
        yield i, dict(x=a1 & 0x1FF, y=a0 & 0xFF, w=w, h=h, off=(a2 & 0x3FF) * gran, pal=a2 >> 12)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prefix")
    ap.add_argument("ids", nargs="+", type=int)
    ap.add_argument("--engine", default="A")
    ap.add_argument("--png")
    a = ap.parse_args()
    vram = Path(a.prefix + ".vram.bin").read_bytes()
    obj = vram[0xA0000:0xE0000] if a.engine == "A" else vram[0xE0000:]
    pal_raw = Path(a.prefix + ".pal.bin").read_bytes()[(0x200 if a.engine == "A" else 0x600):][:0x200]
    files = {p: p.read_bytes() for p in sorted((ROOT / "work/fs/lf2").iterdir())}
    spr = dict(sprites(a.prefix, a.engine))
    imgs = []
    for i in a.ids:
        s = spr[i]
        n = s["w"] * s["h"] // 2
        cell = obj[s["off"]:s["off"] + n]
        hits = [f"{p.stem}+{k:#x}" for p, b in files.items() for k in find_all(b, cell)]
        print(f"sprite {i}: {s['w']}x{s['h']} at {s['x']},{s['y']} pal {s['pal']} VRAM +{s['off']:#x}: "
              + (" ".join(hits) or "no exact copy (compressed or built at run time)"))
        v = np.frombuffer(pal_raw[s["pal"] * 32:][:32], "<u2")
        pal = np.stack([(v & 31) << 3, (v >> 5 & 31) << 3, (v >> 10 & 31) << 3], -1).astype(np.uint8)
        pal[0] = (255, 0, 255)
        t = np.frombuffer(cell, np.uint8)
        px = np.stack([t & 15, t >> 4], -1).reshape(s["h"] // 8, s["w"] // 8, 8, 8).transpose(0, 2, 1, 3)
        imgs.append(pal[px.reshape(s["h"], s["w"])])
    if a.png:
        from PIL import Image
        w = max(im.shape[1] for im in imgs)
        sheet = np.concatenate([np.pad(im, ((0, 2), (0, w - im.shape[1]), (0, 0))) for im in imgs])
        Image.fromarray(sheet).resize((sheet.shape[1] * 6, sheet.shape[0] * 6), Image.NEAREST).save(a.png)
        print(a.png)


def find_all(b, needle):
    k = b.find(needle)
    while k >= 0:
        yield k
        k = b.find(needle, k + 1)


if __name__ == "__main__":
    main()
