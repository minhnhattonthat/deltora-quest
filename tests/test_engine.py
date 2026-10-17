import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402
import fontgen  # noqa: E402


def test_en_tbl_matches_font():
    assert (ROOT / "tbl/en.tbl").read_text(encoding="utf-8").splitlines() == fontgen.table_lines(), \
        "run: python -X utf8 tools/fontgen.py --tbl"


@pytest.mark.skipif(not build.ROM.is_file(), reason="ROM absent")
def test_marker_build_patches_engine():
    orig = build.ROM.read_bytes()
    out = build.build(orig, marker=True)   # asserts original words at every hook site
    assert len(out) == len(orig) and out != orig
