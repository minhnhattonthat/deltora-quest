"""font.py: the dialogue font (FILEDATA file 506, RGCN 4bpp, 16x16 cells, 16 per row, code = cell index).

Pixel values: 1-4 fill (1 brightest), 0xE/0xF outline, 0 transparent (docs/re/text.md).
"""
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FONT_FILE = 506
HDR = 0x30            # RGCN + RAHC headers before the tile data
COLS_TILES = 32       # RAHC width in tiles
NGLYPHS = 1280


def tiles(rgcn):
    return np.frombuffer(rgcn[HDR:], np.uint8)


def glyph(rgcn, code):
    """16x16 array of 4-bit pixel values for `code`."""
    d = rgcn[HDR:]
    out = np.zeros((16, 16), np.uint8)
    gr, gc = divmod(code, 16)
    for ty in range(2):
        for tx in range(2):
            t = (gr * 2 + ty) * COLS_TILES + gc * 2 + tx
            b = np.frombuffer(d[t * 32:t * 32 + 32], np.uint8)
            px = np.stack([b & 15, b >> 4], 1).reshape(8, 8)
            out[ty * 8:ty * 8 + 8, tx * 8:tx * 8 + 8] = px
    return out


def fill(g):
    """Fill weight 0..1 (1 brightest) for the outline font."""
    w = np.zeros(g.shape, np.float32)
    for v, s in ((1, 1.0), (2, 0.8), (3, 0.6), (4, 0.4)):
        w[g == v] = s
    return w
