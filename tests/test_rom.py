import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import check_rom  # noqa: E402

ROM_LINE = next(l for l in (ROOT / "rom.sha1").read_text(encoding="utf-8").splitlines() if l and not l.startswith("#"))
ROM = ROOT / ROM_LINE.split(None, 1)[1]


@pytest.mark.skipif(not ROM.is_file(), reason="ROM absent")
def test_rom_matches_pin():
    check_rom.check()


def test_wrong_hash_rejected(tmp_path):
    bad = tmp_path / "rom.sha1"
    bad.write_text("0" * 40 + "  rom.sha1\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        check_rom.check(bad)
