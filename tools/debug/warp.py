"""warp.py: reach a scene from cold boot and save its state (scene list: tools/debug/scenes.json).

    python -X utf8 tools/debug/warp.py SCENE [--rom build/deltora_en.nds] [--out work/qa/warp]  # shot + sheet + state
    python -X utf8 tools/debug/warp.py --all [--rom ...]     # regenerate every state in work/states/
States land in work/states/<scene>.dst. Regenerate them after any code, font or graphics change (cold boot rule).
"""
import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = Path("C:/Users/Nathan/.claude/plugins/cache/retro-translation/translate-retro-game/d6945f695321/skills/translate-retro-game")
ORIG = ROOT / "rom/1415 - Deltora Quest - 7-tsu no Houseki (J)(Caravan).nds"


def warp(name, scene, rom, out):
    cmd = [sys.executable, "-X", "utf8", str(SKILL / "scripts/emu.py"), str(rom), "--out", str(out),
           "--frames", str(scene["frames"]), "--sheet", "--smoke", "--state-out", str(ROOT / f"work/states/{name}.dst")]
    if "from" in scene:  # continue from another scene's state (made earlier in the same --all run)
        return subprocess.call(cmd + ["--state-in", str(ROOT / f"work/states/{scene['from']}.dst"),
                                      "--route-str", scene["route"], "--shot-every", "30"])
    cmd += ["--route", str(ROOT / scene["route"]), "--shot-every", "300"]
    if scene.get("mash"):
        cmd += ["--mash", "45", "--mash-key", "t128,96"]
    if "warp" in scene:  # [chapter, area]: New Game starts in that stage (tools/debug/warp.lua)
        ch, area = scene["warp"]
        cmd += ["--script", str(ROOT / "tools/debug/warp.lua"), "--var", f"CH={ch}", "--var", f"AREA={area}",
                "--debugger", "--timeout", "1200"]
        if "event" in scene:  # [script file, which LoadExecEvent to replace]: run that event script instead
            cmd += ["--var", f"EV={scene['event'][0]}", "--var", f"EVN={scene['event'][1]}"]
    return subprocess.call(cmd)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scene", nargs="?")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--rom", default=str(ORIG))
    ap.add_argument("--out", default=str(ROOT / "work/qa/warp"))
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()
    scenes = {k: v for k, v in json.loads((ROOT / "tools/debug/scenes.json").read_text(encoding="utf-8")).items()
              if not k.startswith("_")}
    names = list(scenes) if a.all else [a.scene]
    rcs = []
    for wave in ([n for n in names if "from" not in scenes[n]], [n for n in names if "from" in scenes[n]]):
        with ThreadPoolExecutor(a.jobs) as pool:  # each run is its own emulator process and --out dir
            rcs += list(pool.map(lambda n: warp(n, scenes[n], a.rom, Path(a.out) / n), wave))
    names = [n for n in names if "from" not in scenes[n]] + [n for n in names if "from" in scenes[n]]
    bad = [n for n, rc in zip(names, rcs) if rc]
    if bad:
        sys.exit(f"failed: {bad}")


if __name__ == "__main__":
    main()
