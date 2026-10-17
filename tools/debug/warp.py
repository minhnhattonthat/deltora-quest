"""warp.py: reach a scene from cold boot and save its state (scene list: tools/debug/scenes.json).

    python -X utf8 tools/debug/warp.py SCENE [--rom build/deltora_en.nds] [--out work/qa/warp]  # shot + sheet + state
    python -X utf8 tools/debug/warp.py --all [--rom ...]     # regenerate every state in work/states/
States land in work/states/<scene>.dst. Regenerate them after any code, font or graphics change (cold boot rule).
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = Path("C:/Users/Nathan/.claude/plugins/cache/retro-translation/translate-retro-game/d6945f695321/skills/translate-retro-game")
ORIG = ROOT / "rom/1415 - Deltora Quest - 7-tsu no Houseki (J)(Caravan).nds"


def warp(name, scene, rom, out):
    cmd = [sys.executable, "-X", "utf8", str(SKILL / "scripts/emu.py"), str(rom), "--out", str(out),
           "--route", str(ROOT / scene["route"]), "--frames", str(scene["frames"]),
           "--shot-every", "300", "--sheet", "--smoke", "--state-out", str(ROOT / f"work/states/{name}.dst")]
    if scene.get("mash"):
        cmd += ["--mash", "45", "--mash-key", "t128,96"]
    return subprocess.call(cmd)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scene", nargs="?")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--rom", default=str(ORIG))
    ap.add_argument("--out", default=str(ROOT / "work/qa/warp"))
    a = ap.parse_args()
    scenes = {k: v for k, v in json.loads((ROOT / "tools/debug/scenes.json").read_text(encoding="utf-8")).items()
              if not k.startswith("_")}
    names = list(scenes) if a.all else [a.scene]
    bad = [n for n in names if warp(n, scenes[n], a.rom, Path(a.out) / n)]
    if bad:
        sys.exit(f"failed: {bad}")


if __name__ == "__main__":
    main()
