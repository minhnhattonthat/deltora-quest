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


@pytest.mark.skipif(not build.ROM.is_file(), reason="ROM absent")
def test_importing_the_original_render_changes_nothing(tmp_path):
    files = lf2.read(ndspy.rom.NintendoDSRom(build.ROM.read_bytes()).files[build.FILEDATA], [])
    for c, (_, s) in logo.SCREENS.items():
        assert nitro.with_tiles(files[c], nitro.tiles(files[c])[0]) == files[c]
        assert nitro.with_screen(files[s], nitro.screen(files[s])) == files[s]
        png = tmp_path / f"{c}.png"
        Image.fromarray(logo.original(files, c)).save(png)
        assert logo.import_png(files, c, png) == (files[c], files[s])


@pytest.mark.skipif(not build.ROM.is_file(), reason="ROM absent")
def test_logo_import_matches_png():
    files = lf2.read(ndspy.rom.NintendoDSRom(build.ROM.read_bytes()).files[build.FILEDATA], [])
    for c, (_, s) in logo.SCREENS.items():
        png = logo.GFX / f"logo_{c}.png"
        f2 = list(files)
        f2[c], f2[s] = logo.import_png(files, c, png)
        err = np.abs(logo.original(f2, c).astype(int) - np.array(Image.open(png)).astype(int)).mean()
        assert err < 1.5, f"{c}: mean error {err:.2f} after 16-colour re-encode"
