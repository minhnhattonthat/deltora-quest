"""build.py: original ROM -> build/deltora_en.nds.

    python -X utf8 tools/build.py [--out PATH]
"""
import argparse
import sys
from pathlib import Path

import ndspy.rom

sys.path.insert(0, str(Path(__file__).resolve().parent))
import banners  # noqa: E402
import cards  # noqa: E402
import check_rom  # noqa: E402
import codepatch  # noqa: E402
import fontgen  # noqa: E402
import lf2  # noqa: E402
import logo  # noqa: E402
import menu  # noqa: E402
import sprites  # noqa: E402
import tags  # noqa: E402
import text  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom/1415 - Deltora Quest - 7-tsu no Houseki (J)(Caravan).nds"
FILEDATA = 5  # NitroFS file id of FILEDATA.BIN


def build(orig, lang=None, marker=False):
    """Returns the built ROM bytes. lang=None: no edits, equals `orig` (tests/test_identity.py)."""
    rom = ndspy.rom.NintendoDSRom(orig)
    pads = []
    files = lf2.read(rom.files[FILEDATA], pads)
    if lang or marker:
        text.insert(files, lang, marker)
        for n in fontgen.FONTS:
            files[n], adv = fontgen.apply(files[n])
        widths = bytearray(codepatch.NWIDTH)
        for code, w in adv.items():
            widths[code] = w
        rom.arm9 = codepatch.apply(rom.arm9, bytes(widths))
        tags.apply(files)
        logo.apply(files)
        cards.apply(files)
        menu.apply(files)
        banners.apply(files)
        sprites.apply(files)
    rom.files[FILEDATA] = lf2.build(files, pads)
    out = bytearray(rom.save())
    out[0x1000:0x1004] = orig[0x1000:0x1004]  # ndspy writes a size word into this zero gap
    assert len(out) <= len(orig), "ROM grew past the original 128 MiB cartridge"
    return bytes(out + b"\xff" * (len(orig) - len(out)))  # original is 0xFF-padded to the cartridge size


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path)
    ap.add_argument("--marker", action="store_true", help="every line becomes '[id] ...' (phase 5 marker build)")
    args = ap.parse_args()
    out = args.out or ROOT / ("build/deltora_marker.nds" if args.marker else "build/deltora_en.nds")
    check_rom.check()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(build(ROM.read_bytes(), lang=text.LANG, marker=args.marker))
    print(out)


if __name__ == "__main__":
    main()
