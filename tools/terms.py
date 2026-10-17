"""terms.py: candidate glossary terms from the script: katakana runs and 『』-quoted terms, with counts and an example.

    python -X utf8 tools/terms.py OUT.tsv [--min 2]
"""
import argparse
import collections
import re

import text

KATA = re.compile(r"[ァ-ヺー•・]{2,}")
QUOTED = re.compile(r"『(?:\{c[12]\})?([^』{]+)")
SKIP = {"ー", "ーー"}

ap = argparse.ArgumentParser()
ap.add_argument("out")
ap.add_argument("--min", type=int, default=2)
a = ap.parse_args()
count, example = collections.Counter(), {}
for rows in text.load_script().values():
    for e in rows:
        jp = e["jp"].replace("{n}", "").replace("{sp}", " ")
        for m in KATA.findall(jp) + QUOTED.findall(jp):
            m = m.strip("ー•・ ")
            if len(m) < 2 or m in SKIP:
                continue
            count[m] += 1
            example.setdefault(m, f"{e['id']}: {jp[:60]}")
with open(a.out, "w", encoding="utf-8", newline="\n") as f:
    for t, n in count.most_common():
        if n >= a.min or "『" in example[t]:
            f.write(f"{t}\t{n}\t{example[t]}\n")
print(sum(1 for _ in open(a.out, encoding="utf-8")), "terms")
