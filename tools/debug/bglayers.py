"""bglayers.py: render each text BG layer of a dump (tools/debug/dump_at.lua) on its own, to see which layer and
which tiles carry some text. 4bpp, 256x256 text maps (what this game's 2D screens use).

    python -X utf8 tools/debug/bglayers.py work/qa/dump_menu_item/dump_000060 [--engine A] OUT.png
"""
import argparse
import struct
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import nitro  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prefix")
    ap.add_argument("out")
    ap.add_argument("--engine", default="A")
    a = ap.parse_args()
    vram = Path(a.prefix + ".vram.bin").read_bytes()
    base = 0 if a.engine == "A" else 0x80000
    io = Path(a.prefix + ".io.bin").read_bytes()[0 if a.engine == "A" else 0x60:]
    dispcnt = struct.unpack_from("<I", io, 0)[0]
    pal = Path(a.prefix + ".pal.bin").read_bytes()[0 if a.engine == "A" else 0x400:][:0x200]
    v = np.frombuffer(pal, "<u2")
    pal = np.stack([(v & 31) << 3, (v >> 5 & 31) << 3, (v >> 10 & 31) << 3], -1).astype(np.uint8)
    cb, sb = ((dispcnt >> 24) & 7) * 0x10000, ((dispcnt >> 27) & 7) * 0x10000  # engine A only; B ignores them
    if a.engine == "B":
        cb = sb = 0
    layers = []
    for i, cnt in enumerate(struct.unpack_from("<4H", io, 8)):
        chr0 = base + cb + ((cnt >> 2) & 15) * 0x4000
        scr0 = base + sb + ((cnt >> 8) & 31) * 0x800
        raw = np.frombuffer(vram[chr0:chr0 + 0x8000], np.uint8)
        til = np.stack([raw & 15, raw >> 4], -1).reshape(-1, 8, 8)
        scr = np.frombuffer(vram[scr0:scr0 + 0x800], "<u2").reshape(32, 32)
        img = nitro.render(pal, til, scr, 4)
        on = (dispcnt >> (8 + i)) & 1
        print(f"BG{i} cnt {cnt:04X} chr {chr0:#x} scr {scr0:#x} prio {cnt & 3} {'on' if on else 'off'}")
        layers.append(img[:192])
    from PIL import Image
    sheet = np.concatenate([np.pad(l, ((0, 0), (0, 4), (0, 0))) for l in layers], 1)
    Image.fromarray(sheet).save(a.out)
    print(a.out)


if __name__ == "__main__":
    main()
