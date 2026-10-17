"""batches.py: translation batches for agents (docs/translator-brief.md).

    python -X utf8 tools/batches.py split [--size 120]       # work/batches/bNNN.tsv + bNNN.terms.md for untranslated lines
    python -X utf8 tools/batches.py fit "Some text{n}line two" [--portrait]   # px per line, as the lint counts
    python -X utf8 tools/batches.py check bNNN                # validate work/batches/bNNN.out.tsv; prints OK or errors
    python -X utf8 tools/batches.py merge bNNN                # check, then write `en` into script/*.json
Input TSV: id, speaker, form, limit, jp (with the script's {n} {p} {var} ... tokens). Output TSV: id<TAB>EN.
"""
import argparse
import json
import re
import sys
from pathlib import Path

import fontgen
import lint
import text

ROOT = text.ROOT
DIR = ROOT / "work/batches"
SPEAKERS = {"01": "Lief", "02": "Barda", "03": "Jasmine", "05": "Narrator"}
MENU_FILES = {"2191", "2196", "2197"}
SYSTEM_FILES = {"2192", "2194", "2195", "2198", "2199", "2200"}


def form(e):
    if e["hdr"][4:] != "0000":
        return "dlg"
    f = e["id"][:4]
    return "menu" if f in MENU_FILES else "system" if f in SYSTEM_FILES else "narration"


def speaker(e):
    if e["hdr"][4:] == "0000":
        return "-"
    return SPEAKERS.get(e["hdr"][4:6], f"NPC(p{e['hdr'][4:6]})")


def limit(e):
    if form(e) == "dlg":
        return f"{lint.LIMIT_PX}px x{lint.PORTRAIT_LINES} lines/page"
    jp_lines = max(len(p) for p in lint.pages(e["jp"]))
    return f"{lint.LIMIT_PX}px x{jp_lines} lines/page"


def glossary_rows():
    """(jp, en, avoid list) from glossary.md tables (JP | EN | ... | Avoid)."""
    rows = []
    for line in (ROOT / "glossary.md").read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and line.startswith("|") and cells[0] not in ("JP", "") and not set(cells[0]) <= set("-: "):
            avoid = [a.strip() for a in cells[-1].split(",") if a.strip()] if len(cells) >= 5 else []
            rows.append((cells[0], cells[1], avoid))
    return rows


def all_entries():
    return {e["id"]: e for rows in text.load_script().values() for e in rows}


def split(size):
    DIR.mkdir(parents=True, exist_ok=True)
    todo = [e for e in all_entries().values() if not e.get(text.LANG)]
    gl = glossary_rows()
    n = len(list(DIR.glob("b*.tsv")))
    for k in range(0, len(todo), size):
        part = todo[k:k + size]
        name = f"b{n + k // size:03d}"
        if (DIR / f"{name}.tsv").exists():
            sys.exit(f"{name}.tsv exists: batches are split once; delete work/batches to re-split")
        with open(DIR / f"{name}.tsv", "w", encoding="utf-8", newline="\n") as f:
            for e in part:
                f.write("\t".join([e["id"], speaker(e), form(e), limit(e), e["jp"]]) + "\n")
        jp_all = "".join(e["jp"] for e in part)
        terms = [f"| {j} | {en} | {', '.join(av)} |" for j, en, av in gl if j in jp_all]
        (DIR / f"{name}.terms.md").write_text("| JP | EN | Avoid |\n|---|---|---|\n" + "\n".join(terms) + "\n",
                                               encoding="utf-8", newline="\n")
        print(name, len(part), "lines,", len(terms), "terms")


def fit(s, portrait):
    _, adv = fontgen.apply(text.rom_files()[fontgen.FONTS[0]])
    for i, pg in enumerate(lint.pages(s)):
        for ln in pg:
            px = lint.line_px(ln, adv)
            print(f"page {i + 1}: {px:3d}px {'OVER ' if px > lint.LIMIT_PX else ''}{ln}")
        if portrait and len(pg) > lint.PORTRAIT_LINES:
            print(f"page {i + 1}: {len(pg)} lines > {lint.PORTRAIT_LINES} (dialogue box)")


def read_out(name):
    out = {}
    for n, line in enumerate((DIR / f"{name}.out.tsv").read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        if "\t" not in line:
            raise ValueError(f"line {n}: no tab")
        i, en = line.split("\t", 1)
        if i in out:
            raise ValueError(f"line {n}: duplicate id {i}")
        out[i] = en
    return out


def check(name):
    ents = all_entries()
    want = [l.split("\t")[0] for l in (DIR / f"{name}.tsv").read_text(encoding="utf-8").splitlines() if l]
    errs = []
    try:
        out = read_out(name)
    except (OSError, ValueError) as x:
        return [str(x)], {}
    missing, extra = set(want) - set(out), set(out) - set(want)
    if missing or extra:
        errs.append(f"ids: missing {sorted(missing)[:5]} extra {sorted(extra)[:5]}")
    _, adv = fontgen.apply(text.rom_files()[fontgen.FONTS[0]])
    t, gl = text.table("en"), glossary_rows()
    for i, en in out.items():
        if i not in ents:
            continue
        if not en.isascii() or "\\" in en or "\t" in en:
            errs.append(f"{i}: non-ASCII, backslash or tab (use {{n}} for breaks, plain ASCII)")
        e = dict(ents[i], **{text.LANG: en})
        lerrs, _ = lint.check(e, adv, t)
        errs += [f"{i}: {x}" for x in lerrs]
        for j, gen, avoid in gl:
            if j in e["jp"] and gen and gen.lower() not in en.lower() and not gen.startswith("("):
                errs.append(f"{i}: glossary: JP has {j}, EN lacks '{gen}'")
            for av in avoid:
                if re.search(rf"\b{re.escape(av)}\b", en):
                    errs.append(f"{i}: glossary: avoid '{av}'")
    return errs, out


def merge(name):
    errs, out = check(name)
    if errs:
        print("\n".join(errs))
        sys.exit(f"{name}: {len(errs)} errors, not merged")
    for n in text.TEXT_FILES:
        path = text.SCRIPT / f"{n}.json"
        rows = json.loads(path.read_text(encoding="utf-8"))
        hit = False
        for e in rows:
            if e["id"] in out:
                e[text.LANG] = out[e["id"]]
                hit = True
        if hit:
            path.write_text(json.dumps(rows, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"{name}: merged {len(out)} lines")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["split", "fit", "check", "merge"])
    ap.add_argument("arg", nargs="?")
    ap.add_argument("--size", type=int, default=120)
    ap.add_argument("--portrait", action="store_true")
    a = ap.parse_args()
    if a.cmd == "split":
        split(a.size)
    elif a.cmd == "fit":
        fit(a.arg, a.portrait)
    elif a.cmd == "check":
        errs, _ = check(a.arg)
        print("\n".join(errs) if errs else "OK")
        sys.exit(1 if errs else 0)
    else:
        merge(a.arg)
