# Deltora Quest: 7-tsu no Houseki (NDS) English translation

Skill: translate-retro-game (Claude Code: plugin, enabled in .claude/settings.json; other agents: `C:/Users/Nathan/.claude/plugins/cache/retro-translation/translate-retro-game/d6945f695321/skills/translate-retro-game/SKILL.md`; `$SKILL` = the directory holding its SKILL.md). Read it before ROM, text or QA work.

## Commands (run from repo root)
- Build:    `python -X utf8 tools/build.py`  -> build/deltora_en.nds (checks the dump against `rom.sha1` first)
- Check:    `python -X utf8 tools/check.py`  (tests + lint; the pre-commit hook runs this)
- Smoke:    `python -X utf8 $SKILL/scripts/emu.py build/deltora_en.nds --out work/qa/smoke --route tools/routes/boot.txt --smoke`
- Warp:     `python -X utf8 $SKILL/scripts/emu.py build/deltora_en.nds --out work/qa/warp --script tools/debug/warp.lua --var "SCENE='<name>'" --frames 900 --sheet` (scenes: `tools/debug/scenes.json`; never ask the user to play to a scene)
- Release:  `python -X utf8 tools/release.py` (xdelta patch + verify; never publish without the user)

## Paths
- Original ROM: `rom/1415 - Deltora Quest - 7-tsu no Houseki (J)(Caravan).nds` (gitignored; SHA-1 in `rom.sha1`, checked by `tools/check_rom.py`). Emulator: this repo's own DeSmuME QA fork in `tools/desmume/` (release `qa-2`, https://github.com/minhnhattonthat/desmume/releases/download/qa-2/desmume-qa-51b26329-win64.zip; gitignored; settings in `tools/emu-config/`). Savestates: `work/states/`.
- Text: `script/` (format TBD in phase 4). Tables: `tbl/`. Glossary: `glossary.md`. RE notes index: `docs/re/README.md`. Fonts and their licences: `docs/fonts.md`.

## Rulings
- Edit source files (.py .lua .asm .tbl .json) only with the file-edit tool; scripts here read and analyse, never `.replace()` and write back.
- The user's decisions, with the options and reasons: `docs/decisions.md`. Read it before asking the user anything; add each new ruling there the same session.
- Names come from the English Deltora Quest novels (Emily Rodda), not romanized katakana. See `glossary.md`.
- Intro movie: Start/A don't skip it; a touch (`t128,96`) does.

## Status
`docs/status.md`: done, next, open bugs. Update it at the end of every session.
