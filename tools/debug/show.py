"""show.py: show script lines in a real in-game text window (text viewer, tools/debug/textview.lua).

    python -X utf8 tools/debug/show.py 2179_000 2192_003 ... [--rom build/deltora_en.nds] [--lang jp|en]
           [--state work/states/<scene>.dst] [--frames 1500] [--out work/qa/show]
Each text window the game opens after the state loads shows the next id instead. Touch-mash advances dialogue.
Shots: OUT/f*.png plus a sheet.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import text  # noqa: E402

SKILL = Path("C:/Users/Nathan/.claude/plugins/cache/retro-translation/translate-retro-game/d6945f695321/skills/translate-retro-game")
ORIG = ROOT / "rom/1415 - Deltora Quest - 7-tsu no Houseki (J)(Caravan).nds"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="+")
    ap.add_argument("--rom", default=str(ORIG))
    ap.add_argument("--lang", default="jp")
    ap.add_argument("--state", default=str(ROOT / "work/states/dialogue.dst"))
    ap.add_argument("--frames", type=int, default=1500)
    ap.add_argument("--out", default=str(ROOT / "work/qa/show"))
    a = ap.parse_args()
    t = text.table(a.lang)
    rows = {}
    for p in (ROOT / "script").glob("*.json"):
        rows.update({e["id"]: e for e in json.loads(p.read_text(encoding="utf-8"))})
    bodies = [text.encode(t, rows[i][a.lang] or rows[i]["jp"]) for i in a.ids]
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    gen = out / "_strs.lua"
    gen.write_text("STRS = {\n" + "".join("{" + ",".join(map(str, b)) + "},\n" for b in bodies) + "}\n"
                   + "STR_IDS = {" + ",".join(f'"{i}"' for i in a.ids) + "}\n", encoding="utf-8", newline="\n")
    sys.exit(subprocess.call([sys.executable, "-X", "utf8", str(SKILL / "scripts/emu.py"), a.rom, "--out", str(out),
                              "--state-in", a.state, "--frames", str(a.frames), "--mash", "45", "--mash-key", "t128,96",
                              "--script", str(gen), "--script", str(ROOT / "tools/debug/textview.lua"),
                              "--shot-every", "60", "--sheet", "--debugger"]))


if __name__ == "__main__":
    main()
