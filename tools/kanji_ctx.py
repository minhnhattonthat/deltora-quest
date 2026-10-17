"""kanji_ctx.py: per-code usage contexts for checking the kanji table by eye.

    python -X utf8 tools/kanji_ctx.py OUTDIR [--chunk 128]
For each chunk of used codes (0x140+): OUTDIR/ctx_<lo>.txt (code, current table char, OCR top-5, up to 3 lines of
script around it, the code itself shown as 【char】) and OUTDIR/sheet_<lo>_<n>.png (font_sheet.py).
"""
import argparse
import collections
import json
import subprocess
import sys
from pathlib import Path

import text

ap = argparse.ArgumentParser()
ap.add_argument("out")
ap.add_argument("--chunk", type=int, default=128)
a = ap.parse_args()
out = Path(a.out)
out.mkdir(parents=True, exist_ok=True)
t = text.table()
files = text.rom_files()
use = collections.defaultdict(list)
for n in text.TEXT_FILES:
    for i, (_, body) in enumerate(text.split(files[n])):
        codes = [int.from_bytes(body[k:k + 2], "little") for k in range(0, len(body), 2)]
        for k, c in enumerate(codes):
            if 0x140 <= c < 0x500 and len(use[c]) < 3:
                s = [t.decode(x.to_bytes(2, "little"), 0, 2)[0] for x in codes[max(0, k - 12):k + 13]]
                s[min(k, 12)] = f"【{s[min(k, 12)]}】"
                use[c].append(f"{n}_{i:03d}: " + "".join(s).replace("{end}", ""))
ocr = {int(r.split("\t")[0], 16): r.split("\t")[3] for r in (text.ROOT / "work/ocr.tsv").read_text(encoding="utf-8").splitlines()}
codes = sorted(use)
print(len(codes), "kanji codes used")
for lo in range(0, len(codes), a.chunk):
    part = codes[lo:lo + a.chunk]
    name = f"{part[0]:03X}"
    with open(out / f"ctx_{name}.txt", "w", encoding="utf-8", newline="\n") as f:
        for c in part:
            cur = t.decode(c.to_bytes(2, "little"), 0, 2)[0]
            f.write(f"{c:03X}\tcurrent={cur}\tocr={ocr.get(c, '')}\n")
            for u in use[c]:
                f.write(f"\t{u}\n")
    # sheets cover the code span of this chunk, 64 cells each
    for k, s in enumerate(range(part[0], part[-1] + 1, 64)):
        subprocess.run([sys.executable, "-X", "utf8", str(text.ROOT / "tools/font_sheet.py"),
                        str(out / f"sheet_{name}_{k}.png"), "--from", hex(s), "--count", str(min(64, part[-1] + 1 - s)),
                        "--tbl", str(text.ROOT / "tbl/jp.tbl")], check=True, capture_output=True)
