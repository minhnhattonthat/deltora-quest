"""unpack.py: original ROM -> work/fs/ (arm9.bin, ov0-3.bin, lf2/NNNN.bin) for recon.

    python -X utf8 tools/unpack.py [OUTDIR]
"""
import sys
from pathlib import Path

import ndspy.rom

import build
import lf2

out = Path(sys.argv[1] if len(sys.argv) > 1 else build.ROOT / "work/fs")
(out / "lf2").mkdir(parents=True, exist_ok=True)
rom = ndspy.rom.NintendoDSRom(build.ROM.read_bytes())
(out / "arm9.bin").write_bytes(rom.arm9)
for i, ov in rom.loadArm9Overlays().items():
    (out / f"ov{i}.bin").write_bytes(ov.data)
for i, f in enumerate(lf2.read(rom.files[build.FILEDATA])):
    (out / "lf2" / f"{i:04d}.bin").write_bytes(f)
print(out)
