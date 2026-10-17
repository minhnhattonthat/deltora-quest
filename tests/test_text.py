import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402
import text  # noqa: E402

pytestmark = pytest.mark.skipif(not build.ROM.is_file(), reason="ROM absent")


@pytest.fixture(scope="module")
def files():
    return text.rom_files()


def test_split_join_identical(files):
    for n in text.TEXT_FILES:
        assert text.join(text.split(files[n])) == files[n], n


def test_decode_encode_roundtrip(files):
    t = text.table()
    for n in text.TEXT_FILES:
        for i, (_, body) in enumerate(text.split(files[n])):
            assert text.encode(t, text.decode(t, body)) == body, f"{n}_{i:03d}"


def test_no_unknown_codes(files):
    t = text.table()
    bad = [f"{n}_{i:03d}" for n in text.TEXT_FILES for i, (_, b) in enumerate(text.split(files[n]))
           if "[" in text.decode(t, b)]
    assert not bad, bad[:10]
