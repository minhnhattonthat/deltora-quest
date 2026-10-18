import sys
from pathlib import Path

import ndspy.rom
import numpy as np
import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402
import cards  # noqa: E402
import lf2  # noqa: E402


@pytest.mark.skipif(not build.ROM.is_file(), reason="ROM absent")
def test_card_import_matches_png():
    files = lf2.read(ndspy.rom.NintendoDSRom(build.ROM.read_bytes()).files[build.FILEDATA], [])
    f2 = list(files)
    cards.apply(f2)  # raises StopIteration if a card runs out of spare tiles
    for s in cards.CARDS:
        want = np.array(Image.open(cards.GFX / f"card_{s}.png")).astype(int)
        assert np.abs(cards.original(f2, s).astype(int) - want).mean() < 1.0, s
    for s in cards.OVER:
        want = np.array(Image.open(cards.GFX / f"card_{s}.png")).astype(int)
        assert np.abs(cards.original_over(f2, s).astype(int) - want).mean() < 1.5, s
