"""build.py: original ROM -> build/deltora_en.nds.

    python -X utf8 tools/build.py [--out PATH]
"""
import argparse
import sys
from pathlib import Path

import ndspy.rom

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_rom  # noqa: E402
import lf2  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom/1415 - Deltora Quest - 7-tsu no Houseki (J)(Caravan).nds"
FILEDATA = 5  # NitroFS file id of FILEDATA.BIN


def build(orig):
    """Returns the built ROM bytes. With no edits it equals `orig` (tests/test_identity.py)."""
    rom = ndspy.rom.NintendoDSRom(orig)
    pads = []
    files = lf2.read(rom.files[FILEDATA], pads)
    rom.files[FILEDATA] = lf2.build(files, pads)
    out = bytearray(rom.save())
    out[0x1000:0x1004] = orig[0x1000:0x1004]  # ndspy writes a size word into this zero gap
    assert len(out) <= len(orig), "ROM grew past the original 128 MiB cartridge"
    return bytes(out + b"\xff" * (len(orig) - len(out)))  # original is 0xFF-padded to the cartridge size


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=ROOT / "build/deltora_en.nds", type=Path)
    args = ap.parse_args()
    check_rom.check()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(build(ROM.read_bytes()))
    print(args.out)


if __name__ == "__main__":
    main()
