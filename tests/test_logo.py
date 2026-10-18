import sys
from pathlib import Path

import ndspy.rom
import numpy as np
import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402
import lf2  # noqa: E402
import logo  # noqa: E402
import nitro  # noqa: E402


@pytest.fixture(scope="module")
def files():
    if not build.ROM.is_file():
        pytest.skip("ROM absent")
    return lf2.read(ndspy.rom.NintendoDSRom(build.ROM.read_bytes()).files[build.FILEDATA], [])


def test_importing_the_original_render_changes_nothing(files):
    for c, (p, ss) in logo.SCREENS.items():
        assert nitro.with_tiles(files[c], nitro.tiles(files[c])[0]) == files[c]
        for s in ss:
            assert nitro.with_screen(files[s], nitro.screen(files[s])) == files[s]
        targets = [logo.original(files, c, s) for s in ss]
        assert nitro.import_screens(files[c], files[p], [files[s] for s in ss], targets) == \
            (files[c], [files[s] for s in ss])


def test_logo_import_matches_every_screen(files):
    f2 = list(files)
    logo.apply(f2)
    for c, (_, ss) in logo.SCREENS.items():
        for s in ss:
            want = np.array(Image.open(logo.GFX / f"logo_{s}.png")).astype(int)
            err = np.abs(logo.original(f2, c, s).astype(int) - want).mean()
            assert err < 1.5, f"screen {s}: mean error {err:.2f} after 16-colour re-encode"


def test_shared_tiles_stay_consistent():
    """Two screens showing one tile: a cell changed on one screen only gets its own tile."""
    rgcn, rlcn, rcsn = (nitro.load(n) for n in (1620, 1621, 1622))
    til, _ = nitro.tiles(rgcn)
    scr = nitro.screen(rcsn)
    pal = nitro.palette(rlcn)
    old = nitro.render(pal, til, scr, 4)
    tgt = old.copy()
    tgt[0:8, 0:8] = pal[16 * (scr[0, 0] >> 12) + 1]  # one cell, solid colour 1
    new_rgcn, (a, b) = nitro.import_screens(rgcn, rlcn, [rcsn, rcsn], [tgt, old])
    t2, _ = nitro.tiles(new_rgcn)
    assert (nitro.render(pal, t2, nitro.screen(a), 4) == tgt).all()
    assert (nitro.render(pal, t2, nitro.screen(b), 4) == old).all()
