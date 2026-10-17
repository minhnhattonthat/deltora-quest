import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import lint  # noqa: E402
import text  # noqa: E402

ADV = {fontgen_code: 6 for fontgen_code in range(0x10, 0x70)}


def run(jp, en, hdr="00000104"):
    return lint.check({"id": "t", "hdr": hdr, "jp": jp, text.LANG: en}, ADV, text.table("en"))


def test_clean_line():
    assert run("こんにちは", "Hello there.") == ([], [])


def test_errors():
    errs, _ = run("{var}こ", "You got {var}th place, こ")
    assert any("Japanese" in e for e in errs) and any("ordinal" in e for e in errs)
    errs, _ = run("{c2}A{/c}", "A")
    assert any("control codes" in e for e in errs)
    errs, _ = run("あ", "a{n}b{n}c")              # portrait box shows 2 lines
    assert any("portrait" in e for e in errs)
    errs, _ = run("あ", "x" * 41)                  # 41 x 6 px > 240
    assert any("px" in e for e in errs)


def test_unmeasured_window_warns():
    _, warns = run("あ{n}い", "one line{n}two lines{n}three lines", hdr="00000000")
    assert [k for k, _ in warns] == ["more lines than JP"]
