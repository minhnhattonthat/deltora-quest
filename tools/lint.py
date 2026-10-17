"""lint.py: check every translated line against the window budgets (docs/re/windows.md).

    python -X utf8 tools/lint.py [--all]     # errors exit 1; warnings summarised (--all lists them)
Errors: not encodable, Japanese left, control codes ({var} {c1} {c2} {/c} {f6} {f9} {iconN}) differ from the JP,
a line wider than its window, more lines on a page than the window shows, an ordinal suffix glued to {var}.
Warnings: more lines per page than the JP had in an unmeasured window, a stub last line (< 6 chars).
"""
import argparse
import collections
import re
import sys

import fontgen
import text

LIMIT_PX = 240          # measured: portrait box and narration show 256 px, centred; 8 px margin each side
PORTRAIT_LINES = 2      # measured: a 3rd line falls below the box
SP_PX = 6               # {sp} = half the window's 12 px pitch
KEEP = re.compile(r"\{(var|c1|c2|/c|f6|f9|icon\d)\}")
TOKEN = re.compile(r"\{[^}]*\}")
JP = re.compile(r"[぀-ヿ一-鿿]")


def is_portrait(hdr):
    """Portrait dialogue box: header word 2 slot (low byte) set, except 00 (picture narration) and 05 (narrator:
    book/letter narration window, measured 4+ lines)."""
    return hdr[4:8] != "0000" and hdr[4:6] not in ("00", "05")


def line_px(line, adv):
    px = 0
    for tok in re.split(r"(\{[^}]*\})", line):
        if tok == "{sp}":
            px += SP_PX
        elif tok.startswith("{"):
            continue
        else:
            px += sum(adv.get(fontgen.code_of(c), 12) for c in tok)
    return px


def pages(s):
    return [p.split("{n}") for p in s.split("{p}")]


def check(e, adv, t):
    errs, warns = [], []
    en, jp = e.get(text.LANG, ""), e["jp"]
    if not en:
        return errs, warns
    try:
        text.encode(t, en)
    except Exception as x:  # noqa: BLE001 - report any encode failure as a lint error
        errs.append(f"not encodable: {x}")
    if JP.search(en):
        errs.append("Japanese left")
    if collections.Counter(KEEP.findall(en)) != collections.Counter(KEEP.findall(jp)):
        errs.append(f"control codes {sorted(KEEP.findall(jp))} -> {sorted(KEEP.findall(en))}")
    if re.search(r"\{var\}(st|nd|rd|th)\b", en):
        errs.append("ordinal suffix after {var}")
    portrait = is_portrait(e["hdr"])
    jp_lines = max(len(p) for p in pages(jp))
    for pg in pages(en):
        for ln in pg:
            if line_px(ln, adv) > LIMIT_PX:
                errs.append(f"{line_px(ln, adv)} px > {LIMIT_PX}: {ln[:40]}")
        if portrait and len(pg) > PORTRAIT_LINES:
            errs.append(f"{len(pg)} lines on a portrait page (max {PORTRAIT_LINES})")
        elif not portrait and len(pg) > jp_lines:
            warns.append(("more lines than JP", f"{len(pg)} lines on a page, JP had {jp_lines} (window not measured)"))
        if len(pg) > 1 and len(TOKEN.sub("", pg[-1]).strip()) < 6:
            warns.append(("stub last line", repr(pg[-1])))
    return errs, warns


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    _, adv = fontgen.apply(text.rom_files()[fontgen.FONTS[0]])
    t = text.table("en")
    n_err, warns, done = 0, collections.Counter(), 0
    for rows in text.load_script().values():
        for e in rows:
            done += bool(e.get(text.LANG))
            errs, ws = check(e, adv, t)
            for x in errs:
                print(f"ERROR {e['id']}: {x}")
            n_err += len(errs)
            for kind, msg in ws:
                warns[kind] += 1
                if a.all:
                    print(f"warn  {e['id']}: {kind}: {msg}")
    print(f"lint: {done} translated lines, {n_err} errors, {sum(warns.values())} warnings"
          + (f" ({dict(warns)})" if warns else ""))
    return 1 if n_err else 0


if __name__ == "__main__":
    sys.exit(main())
