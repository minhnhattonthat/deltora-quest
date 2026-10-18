import sys
from pathlib import Path

import ndspy.rom
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
