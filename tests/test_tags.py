import sys
from pathlib import Path

import ndspy.rom
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402
import lf2  # noqa: E402
import tags  # noqa: E402


def test_every_tag_fits():
    for name in tags.NAMES.values():
        tags.draw(name)  # asserts the width


@pytest.mark.skipif(not build.ROM.is_file(), reason="ROM absent")
def test_tag_codec_roundtrips():
    files = lf2.read(ndspy.rom.NintendoDSRom(build.ROM.read_bytes()).files[build.FILEDATA], [])
    for n in tags.NAMES:
        f = files[tags.BASE + n]
        assert f[:4] == b"RGCN" and len(f) == tags.HDR + tags.W * tags.H // 2
        assert tags.encode(tags.decode(f), f) == f
