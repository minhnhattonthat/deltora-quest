"""release.py: build, gate, xdelta patch, re-apply check, README, zip -> release/.

    python -X utf8 tools/release.py [--version 0.9]

Gates (any failure stops the release): fresh build from the pinned dump, cold-boot smoke, no Japanese left in the
text files or arm9 (jp_left.py, unchanged runs only), visual-QA gate (qa_gate.py check). The patch is re-applied to
the original and must give the built ROM byte for byte. Publishing is the user's call.
"""
import argparse
import hashlib
import subprocess
import sys
import zipfile
import zlib
from pathlib import Path

import ndspy.rom

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build  # noqa: E402
import check_rom  # noqa: E402
import lf2  # noqa: E402
from debug.warp import SKILL  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release"
TEXT = range(2178, 2201)  # FILEDATA dialogue files
ARM9_KNOWN = ("0x014793 code bytes", "0x059EF7 code bytes")  # jp_left hits in arm9 that are data, not text


def run(cmd, **kw):
    print("$", " ".join(str(c) for c in cmd), flush=True)
    subprocess.run([str(c) for c in cmd], check=True, cwd=ROOT, **kw)


def hashes(data):
    return {"crc32": f"{zlib.crc32(data):08X}", "md5": hashlib.md5(data).hexdigest(), "sha1": hashlib.sha1(data).hexdigest()}


def jp_left(orig, built, tmp):
    """Dump the text files and arm9 of both ROMs and scan them; raises on any unchanged Japanese run."""
    scan = [sys.executable, "-X", "utf8", SKILL / "scripts/jp_left.py"]
    for tag, data in (("orig", orig), ("en", built)):
        rom = ndspy.rom.NintendoDSRom(data)
        files = lf2.read(rom.files[build.FILEDATA])
        (tmp / tag).mkdir(parents=True, exist_ok=True)
        for n in TEXT:
            (tmp / tag / f"{n}.bin").write_bytes(files[n])
        (tmp / tag / "arm9.bin").write_bytes(rom.arm9)
    known = tmp / "arm9_known.txt"
    known.write_text("\n".join(ARM9_KNOWN) + "\n", encoding="utf-8")
    run(scan + [tmp / "en/arm9.bin", "--orig", tmp / "orig/arm9.bin", "--sjis", "--known", known])
    for n in TEXT:
        run(scan + [tmp / f"en/{n}.bin", "--orig", tmp / f"orig/{n}.bin", "--tbl", ROOT / "tbl/jp.tbl", "--le16"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="0.9")
    args = ap.parse_args()
    check_rom.check()
    tmp = OUT / "tmp"
    tmp.mkdir(parents=True, exist_ok=True)

    orig = build.ROM.read_bytes()
    built = build.build(orig, lang=build.text.LANG)
    rom_path = ROOT / "build/deltora_en.nds"
    rom_path.write_bytes(built)

    run([sys.executable, "-X", "utf8", SKILL / "scripts/emu.py", rom_path, "--out", tmp / "smoke",
         "--route", ROOT / "tools/routes/boot.txt", "--smoke"])
    jp_left(orig, built, tmp)
    run([sys.executable, "-X", "utf8", SKILL / "scripts/qa_gate.py", "check", ROOT / "work/qa/manifest.tsv",
         ROOT / "work/qa/verdicts"])

    name = f"Deltora_Quest_7_Houseki_EN_v{args.version}"
    patch = tmp / f"{name}.xdelta"  # no secondary compression: Delta Patcher and xdelta UI builds read plain VCDIFF
    run(["xdelta3", "-f", "-e", "-9", "-S", "none", "-s", build.ROM, rom_path, patch])
    back = tmp / "reapplied.nds"
    run(["xdelta3", "-f", "-d", "-s", build.ROM, patch, back])
    assert back.read_bytes() == built, "re-applied patch differs from the build"
    back.unlink()

    h, p = hashes(orig), hashes(built)
    readme = (ROOT / "docs/release-readme.txt").read_text(encoding="utf-8").format(
        version=args.version, patch=patch.name, rom=build.ROM.name, size=len(orig),
        crc32=h["crc32"], md5=h["md5"], sha1=h["sha1"], pcrc32=p["crc32"], psha1=p["sha1"])
    zpath = OUT / f"{name}.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_STORED) as z:  # xdelta is already compressed
        z.write(patch, patch.name)
        z.writestr("README.txt", readme.replace("\n", "\r\n"))
    print(zpath)


if __name__ == "__main__":
    main()
