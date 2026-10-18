"""gfxsurvey.py: render every RCSN screen in FILEDATA with the nearest RGCN and RLCN before it, into contact sheets,
to find text drawn as graphics without reaching each screen in game (docs/re/graphics.md).

    python -X utf8 tools/debug/gfxsurvey.py [--out work/qa/gfxsurvey] [--per 30]
The pairing is a guess (files come in RLCN/RGCN/RCSN runs); a garbled render just means a wrong guess. Each tile is
labelled scr/chr/pal. 8bpp screens use the whole palette.
"""
import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import nitro  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]


def main():
    from PIL import Image, ImageDraw
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "work/qa/gfxsurvey"))
    ap.add_argument("--per", type=int, default=30)
    a = ap.parse_args()
    d = ROOT / "work/fs/lf2"
    magic = {int(p.stem): p.read_bytes()[:4] for p in d.iterdir()}
    done = []
    for n in sorted(magic):
        if magic[n] != b"RCSN":
            continue
        c = next((k for k in range(n - 1, n - 8, -1) if magic.get(k) == b"RGCN"), None)
        p = next((k for k in range(c - 1, c - 8, -1) if magic.get(k) == b"RLCN"), None) if c else None
        if p is None:
            continue
        try:
            til, bpp = nitro.tiles(nitro.load(c))
            img = nitro.render(nitro.palette(nitro.load(p)), til, nitro.screen(nitro.load(n)), bpp)[:192, :256]
        except Exception as e:  # noqa: BLE001  survey: skip what doesn't decode, list it
            print(f"skip {n}: {e}")
            continue
        done.append((f"{n}/{c}/{p}", img))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for s in range(0, len(done), a.per):
        chunk = done[s:s + a.per]
        cols = 6
        sheet = Image.new("RGB", (cols * 260, -(-len(chunk) // cols) * 206), (30, 30, 30))
        dr = ImageDraw.Draw(sheet)
        for i, (lab, img) in enumerate(chunk):
            x, y = (i % cols) * 260, (i // cols) * 206
            sheet.paste(Image.fromarray(np.ascontiguousarray(img)), (x, y + 12))
            dr.text((x + 2, y), lab, fill=(255, 255, 0))
        path = out / f"sheet_{s // a.per:02}.png"
        sheet.save(path)
        print(path)
    print(len(done), "screens")


if __name__ == "__main__":
    main()
