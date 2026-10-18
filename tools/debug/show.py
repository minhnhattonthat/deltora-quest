"""show.py: show script lines in real in-game text windows (text viewer, tools/debug/textview.lua).

    python -X utf8 tools/debug/show.py 2179_000 "=raw English{n}text" ... [--rom build/deltora_en.nds]
           [--state work/states/<scene>.dst] [--frames 1500] [--mash 45] [--out work/qa/show]
The next text windows the game opens after the state loads show these instead, in order. An id is loaded by the game
itself from --rom (its own name tag and portrait); "=text" is encoded with tbl/en.tbl and keeps the window's
original header. Touch-mash every --mash frames advances dialogue. Shots: OUT/f*.png plus a sheet; log.txt lists
every message load as file_index.
"""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import text  # noqa: E402

SKILL = Path("C:/Users/Nathan/.claude/plugins/cache/retro-translation/translate-retro-game/d6945f695321/skills/translate-retro-game")
ORIG = ROOT / "rom/1415 - Deltora Quest - 7-tsu no Houseki (J)(Caravan).nds"


def entry(item, en):
    if item.startswith("="):
        return "{" + ",".join(map(str, text.encode(en, item[1:]))) + "}"
    f, i = item.split("_")
    return f"{{file={int(f)}, index={int(i)}}}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="+")
    ap.add_argument("--rom", default=str(ORIG))
    ap.add_argument("--state", default=str(ROOT / "work/states/dialogue.dst"))
    ap.add_argument("--frames", type=int, default=1500)
    ap.add_argument("--out", default=str(ROOT / "work/qa/show"))
    ap.add_argument("--mash", default="45", help="frames between touches that advance the text")
    a = ap.parse_args()
    en = text.table("en")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    gen = out / "_strs.lua"
    gen.write_text("STRS = {\n" + "".join(entry(i, en) + ",\n" for i in a.ids) + "}\n"
                   + "STR_IDS = {" + ",".join(f'"{k}"' for k in range(len(a.ids))) + "}\n", encoding="utf-8", newline="\n")
    sys.exit(subprocess.call([sys.executable, "-X", "utf8", str(SKILL / "scripts/emu.py"), a.rom, "--out", str(out),
                              "--state-in", a.state, "--frames", str(a.frames), "--mash", a.mash, "--mash-key", "t128,96",
                              "--script", str(gen), "--script", str(ROOT / "tools/debug/textview.lua"),
                              "--shot-every", "60", "--sheet", "--debugger", "--timeout", "900"]))


if __name__ == "__main__":
    main()
