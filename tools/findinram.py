"""findinram.py: which archive files (work/fs/lf2, work/fs/lz) sit in a RAM dump, and where.

    python -X utf8 tools/findinram.py work/qa/x/ram_000100.bin [--min 64]
Samples 32-byte chunks of each file (skipping low-entropy ones) and reports the RAM address of the file start.
"""
import argparse
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("ram")
ap.add_argument("--min", type=int, default=64, help="skip files smaller than this")
ap.add_argument("--fs", default="work/fs")
a = ap.parse_args()
ram = Path(a.ram).read_bytes()
for sub in ("lf2", "lz", "."):
    for p in sorted(Path(a.fs, sub).glob("*.bin")):
        d = p.read_bytes()
        if len(d) < a.min:
            continue
        for off in range(0, len(d) - 32, max(32, len(d) // 8)):
            k = d[off:off + 32]
            if len(set(k)) < 8:
                continue
            j = ram.find(k)
            if j >= 0:
                print(f"{sub}/{p.name} ({len(d)} B) at {0x02000000 + j - off:#x}")
            break
