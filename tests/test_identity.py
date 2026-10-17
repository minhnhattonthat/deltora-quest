import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402
import lf2  # noqa: E402

pytestmark = pytest.mark.skipif(not build.ROM.is_file(), reason="ROM absent")


@pytest.fixture(scope="module")
def orig():
    return build.ROM.read_bytes()


def test_lf2_repack_identical(orig):
    import ndspy.rom
    data = ndspy.rom.NintendoDSRom(orig).files[build.FILEDATA]
    pads = []
    assert lf2.build(lf2.read(data, pads), pads) == data


def test_rom_rebuild_identical(orig):
    assert build.build(orig) == orig
