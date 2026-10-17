"""winstats.py: Japanese line width / lines-per-page by header, to find the window types and their design budgets.

    python -X utf8 tools/winstats.py [--by w1hi|w2|w1|file]
Width in px at the original fixed pitch (12, {sp} = 6, colour/var codes 0). Prints count, max px, max lines, an example.
"""
import argparse
import collections
import re

import text

PITCH = 12
ZERO = re.compile(r"\{(c1|c2|/c|f6|f9|var|icon\d)\}")


def page_stats(jp):
    px, lines = 0, 0
    for page in jp.split("{p}"):
        ls = page.split("{n}")
        lines = max(lines, len(ls))
        for line in ls:
            line = ZERO.sub("", line).replace("{sp}", "\t")
            px = max(px, sum(PITCH // 2 if c == "\t" else PITCH for c in line))
    return px, lines


def key(e, by):
    w1, w2 = e["hdr"][:4], e["hdr"][4:]
    return {"w1hi": w1[2:], "w2": w2, "w1": w1, "file": e["id"][:4]}[by]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--by", default="w2", choices=["w1hi", "w2", "w1", "file"])
    a = ap.parse_args()
    agg = collections.defaultdict(lambda: [0, 0, 0, ""])
    for rows in text.load_script().values():
        for e in rows:
            px, ln = page_stats(e["jp"])
            g = agg[key(e, a.by)]
            g[0] += 1
            if px > g[1]:
                g[1], g[3] = px, e["id"]
            g[2] = max(g[2], ln)
    for k, (n, px, ln, ex) in sorted(agg.items(), key=lambda kv: -kv[1][0]):
        print(f"{k:6} n={n:5} maxpx={px:4} maxlines={ln} e.g. {ex}")
