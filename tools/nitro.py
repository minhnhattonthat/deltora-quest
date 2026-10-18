"""nitro.py: decode Nitro BG graphics (RLCN palette, RGCN tiles, RCSN screen) from FILEDATA files, render to PNG.

    python -X utf8 tools/nitro.py OUT.png PAL CHR SCR    # FILEDATA numbers, e.g. 464 465 466 (work/fs/lf2)
"""
import struct
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def section(data, magic):
    """Body of the first section after the 0x10 file header (its 8-byte section header stripped)."""
    off = struct.unpack_from("<H", data, 0x0C)[0]
    assert data[off:off + 4] == magic, (data[off:off + 4], magic)
    size = struct.unpack_from("<I", data, off + 4)[0]
    return off, data[off + 8:off + size]


def palette(rlcn):
    _, b = section(rlcn, b"TTLP")
    size, off = struct.unpack_from("<II", b, 8)
    v = np.frombuffer(b[off:off + size], "<u2")
    return np.stack([(v & 31) << 3, (v >> 5 & 31) << 3, (v >> 10 & 31) << 3], -1).astype(np.uint8)


def tiles(rgcn):
    """-> (n, 8, 8) palette indices, bpp"""
    _, b = section(rgcn, b"RAHC")
    bpp = {3: 4, 4: 8}[struct.unpack_from("<I", b, 4)[0]]
    size, off = struct.unpack_from("<II", b, 0x10)
    raw = np.frombuffer(b[off:off + size], np.uint8)
    if bpp == 4:
        raw = np.stack([raw & 15, raw >> 4], -1).reshape(-1)
    return raw.reshape(-1, 8, 8), bpp


def screen(rcsn):
    """-> (rows, cols) u16 map entries"""
    _, b = section(rcsn, b"NRCS")
    w, h, _, size = struct.unpack_from("<HHII", b, 0)
    return np.frombuffer(b[12:12 + size], "<u2").reshape(h // 8, w // 8)


def with_tiles(rgcn, til):
    """rgcn with its 4bpp tile data replaced by til (same count)."""
    off, b = section(rgcn, b"RAHC")
    size, doff = struct.unpack_from("<II", b, 0x10)
    t = til.reshape(-1, 32, 2).astype(np.uint8)
    raw = (t[..., 0] | (t[..., 1] << 4)).tobytes()
    assert len(raw) == size
    start = off + 8 + doff
    return rgcn[:start] + raw + rgcn[start + size:]


def with_screen(rcsn, scr):
    off, b = section(rcsn, b"NRCS")
    size = struct.unpack_from("<I", b, 8)[0]
    raw = scr.astype("<u2").tobytes()
    assert len(raw) == size
    return rcsn[:off + 20] + raw + rcsn[off + 20 + size:]


def render(pal, til, scr, bpp):
    rows, cols = scr.shape
    img = np.zeros((rows * 8, cols * 8, 3), np.uint8)
    for r in range(rows):
        for c in range(cols):
            e = int(scr[r, c])
            t = til[e & 0x3FF] if (e & 0x3FF) < len(til) else np.zeros((8, 8), np.uint8)
            if e & 0x400:
                t = t[:, ::-1]
            if e & 0x800:
                t = t[::-1]
            base = 0 if bpp == 8 else (e >> 12) * 16
            img[r * 8:r * 8 + 8, c * 8:c * 8 + 8] = pal[(base + t) % len(pal)]
    return img


def load(n):
    return (ROOT / f"work/fs/lf2/{n:04}.bin").read_bytes()


def main():
    from PIL import Image
    out, p, c, s = sys.argv[1], *map(int, sys.argv[2:5])
    til, bpp = tiles(load(c))
    Image.fromarray(render(palette(load(p)), til, screen(load(s)), bpp)).save(out)
    print(out, f"{bpp}bpp {len(til)} tiles")


if __name__ == "__main__":
    main()
