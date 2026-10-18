import sys
from pathlib import Path

import ndspy.rom
import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402
import lf2  # noqa: E402
import menu  # noqa: E402
import nitro  # noqa: E402


@pytest.fixture(scope="module")
def files():
    if not build.ROM.is_file():
        pytest.skip("ROM absent")
    return lf2.read(ndspy.rom.NintendoDSRom(build.ROM.read_bytes()).files[build.FILEDATA], [])


def test_every_cell_bank_roundtrips(files):
    for b in files:
        if b[:4] == b"RECN":
            assert nitro.build_recn(nitro.parse_recn(b)) == b


def test_banners_redraw_every_frame(files):
    import banners
    f = list(files)
    banners.apply(f)
    for n in banners.BANNERS:
        r = nitro.parse_recn(f[n])
        new, _ = nitro.tiles(f[n + 1])
        old, _ = nitro.tiles(files[n + 1])
        for cell, (src, _) in zip(r["cells"], r["transfer"]):
            objs, w, h = banners.layout(cell, src // 32, (32 << r["mapping"]) // 32)
            a, b = banners.get(old, objs, w, h), banners.get(new, objs, w, h)
            assert (a != b).any() and set(np.unique(b)) <= set(np.unique(a)) | {0}, n  # changed, same colours


def test_sprite_labels_change_only_their_tiles(files):
    import sprites
    f = list(files)
    sprites.apply(f)  # asserts every label fits
    for n, (c, _, _) in sprites.SPOTS.items():
        assert f[c] != files[c] and len(f[c]) == len(files[c]) and f[c][:0x30] == files[c][:0x30]


def test_menu_repack_is_consistent(files):
    f = list(files)
    menu.apply(f)
    r = nitro.parse_recn(f[menu.RECN])
    for n in (menu.TILED, menu.LINEAR):
        size = len(nitro.section(f[n], b"RAHC")[1]) - 0x18
        assert max(src + sz for src, sz in r["transfer"]) <= size
    assert max(sz for _, sz in r["transfer"]) == r["max_transfer"] == menu.SLICE
    for cell, (_, sz) in zip(r["cells"], r["transfer"]):
        assert len(cell["objs"]) in (1, 3) and sz in (0x200, menu.SLICE)
