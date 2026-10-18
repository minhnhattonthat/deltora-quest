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


def with_data(rgcn, raw):
    """rgcn with its tile data replaced by raw bytes of any length (section and file sizes updated)."""
    off, b = section(rgcn, b"RAHC")
    size, doff = struct.unpack_from("<II", b, 0x10)
    start = off + 8 + doff
    out = bytearray(rgcn[:start] + raw + rgcn[start + size:])
    struct.pack_into("<I", out, off + 8 + 0x10, len(raw))
    struct.pack_into("<I", out, off + 4, struct.unpack_from("<I", rgcn, off + 4)[0] + len(raw) - size)
    struct.pack_into("<I", out, 8, len(out))
    return bytes(out)


def parse_recn(recn):
    """RECN cell bank -> dict: cells [{attr, objs [(a0, a1, a2)]}], mapping, transfer [(src, size)] or None,
    max_transfer, rest (the KBEC fields kept as they are), tail (the sections after KBEC). 8-byte cell entries only."""
    off = struct.unpack_from("<H", recn, 0x0C)[0]
    assert recn[off:off + 4] == b"KBEC"
    ksize = struct.unpack_from("<I", recn, off + 4)[0]
    s = recn[off + 8:off + ksize]
    n, attr, coff, mapping, vt, unk, ext = struct.unpack_from("<HHIIIII", s, 0)
    assert attr & 1 == 0 and ext == 0 and coff == 0x18
    oam0 = coff + n * 8
    cells = []
    for i in range(n):
        nobj, cattr, ooff = struct.unpack_from("<HHI", s, coff + i * 8)
        cells.append({"attr": cattr, "objs": [struct.unpack_from("<HHH", s, oam0 + ooff + k * 6) for k in range(nobj)]})
    transfer, mx = None, 0
    if vt:
        mx, toff = struct.unpack_from("<II", s, vt)
        transfer = [struct.unpack_from("<II", s, vt + toff + i * 8) for i in range(n)]
    return {"head": recn[:off], "attr": attr, "mapping": mapping, "unk": unk, "cells": cells, "transfer": transfer,
            "max_transfer": mx, "tail": recn[off + ksize:]}


def build_recn(r):
    n = len(r["cells"])
    objs, entries, k = b"", b"", 0
    for c in r["cells"]:
        entries += struct.pack("<HHI", len(c["objs"]), c["attr"], k * 6)
        objs += b"".join(struct.pack("<HHH", *o) for o in c["objs"])
        k += len(c["objs"])
    objs += b"\0" * (-len(objs) % 4)
    vt = 0x18 + 8 * n + len(objs) if r["transfer"] is not None else 0
    body = struct.pack("<HHIIIII", n, r["attr"], 0x18, r["mapping"], vt, r["unk"], 0) + entries + objs
    if r["transfer"] is not None:
        body += struct.pack("<II", r["max_transfer"], 8) + b"".join(struct.pack("<II", *t) for t in r["transfer"])
    kbec = b"KBEC" + struct.pack("<I", 8 + len(body)) + body
    out = bytearray(r["head"] + kbec + r["tail"])
    struct.pack_into("<I", out, 8, len(out))
    return bytes(out)


def with_screen(rcsn, scr):
    off, b = section(rcsn, b"NRCS")
    size = struct.unpack_from("<I", b, 8)[0]
    raw = scr.astype("<u2").tobytes()
    assert len(raw) == size
    return rcsn[:off + 20] + raw + rcsn[off + 20 + size:]


def import_screens(rgcn, rlcn, rcsns, targets):
    """Re-encode the 8x8 cells of 4bpp screens rcsns (all using tiles rgcn, palette rlcn) whose pixels in targets
    (RGB arrays, same order, at least the screen's visible rows) differ from the original render. Each changed cell
    gets the palette of the 16 that fits it best (index 0 left unused). Cells that end up identical share one tile; a
    tile is rewritten in place only when every cell that uses it, on any of the screens, changes to the same thing;
    otherwise the cell gets a tile no screen uses. -> (rgcn, [rcsn, ...])"""
    pal, (til, bpp) = palette(rlcn), tiles(rgcn)
    assert bpp == 4
    scrs = [screen(s).copy() for s in rcsns]
    pals = pal.astype(int).reshape(16, 16, 3)[:, 1:]
    refs = {}
    for k, scr in enumerate(scrs):
        for (r, c), e in np.ndenumerate(scr):
            if (e & 0x3FF) < len(til):
                refs.setdefault(int(e) & 0x3FF, set()).add((k, r, c))
    groups = {}  # (palette, tile bytes) -> cells
    for k, (scr, tgt) in enumerate(zip(scrs, targets)):
        old = render(pal, til, scr, 4).astype(int)
        new = np.asarray(tgt).astype(int)
        for r in range(min(len(new), len(old)) // 8):
            for c in range(scr.shape[1]):
                cell = new[r * 8:r * 8 + 8, c * 8:c * 8 + 8]
                if (cell == old[r * 8:r * 8 + 8, c * 8:c * 8 + 8]).all():
                    continue
                d = ((cell[None, :, :, None, :] - pals[:, None, None, :, :]) ** 2).sum(-1)  # (16, 8, 8, 15)
                best = int(d.min(-1).sum((1, 2)).argmin())
                px = (d[best].argmin(-1) + 1).astype(np.uint8)
                groups.setdefault((best, px.tobytes()), set()).add((k, r, c))
    changed = set().union(*groups.values()) if groups else set()
    til = til.copy()
    used = {t for t, cs in refs.items() if not cs <= changed}  # still shown somewhere unchanged
    todo = []
    for key, cells in groups.items():
        olds = sorted({int(scrs[k][r, c]) & 0x3FF for k, r, c in cells})
        own = [t for t in olds if refs.get(t, set()) <= cells and t not in used]
        if own:
            used.add(own[0])
            todo.append((key, cells, own[0]))
        else:
            todo.append((key, cells, None))
    owned = {x[2] for x in todo}
    free = (t for t in range(len(til)) if t not in used and t not in owned)
    for key, cells, t in todo:
        if t is None:
            t = next(free)  # StopIteration here = out of tiles: shrink the edit or dedupe more
            used.add(t)
        best, raw = key
        til[t] = np.frombuffer(raw, np.uint8).reshape(8, 8)
        for k, r, c in cells:
            scrs[k][r, c] = t | (best << 12)  # pixels are as displayed, so no flip bits
    return with_tiles(rgcn, til), [with_screen(s, scr) for s, scr in zip(rcsns, scrs)]


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
