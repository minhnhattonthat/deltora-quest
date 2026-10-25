# Deltora Quest: 7-tsu no Houseki (NDS) English translation

Skill: translate-retro-game (Claude Code: plugin, enabled in .claude/settings.json; other agents: `C:/Users/Nathan/.claude/plugins/cache/retro-translation/translate-retro-game/d6945f695321/skills/translate-retro-game/SKILL.md`; `$SKILL` = the directory holding its SKILL.md). Read it before ROM, text or QA work.

## Commands (run from repo root)
- Build:    `python -X utf8 tools/build.py [--marker]`  -> build/deltora_en.nds / deltora_marker.nds (checks the dump against `rom.sha1` first)
- Font:     edit `fonts/en_font.txt`, then `python -X utf8 tools/fontgen.py --tbl` (regenerates tbl/en.tbl)
- Check:    `python -X utf8 tools/check.py`  (tests + lint; the pre-commit hook runs this)
- Smoke:    `python -X utf8 $SKILL/scripts/emu.py build/deltora_en.nds --out work/qa/smoke --route tools/routes/boot.txt --smoke`
- Warp:     `python -X utf8 tools/debug/warp.py <scene> [--rom build/deltora_en.nds]` (`--all` regenerates work/states; scenes: `tools/debug/scenes.json`; never ask the user to play to a scene)
- Show a line in-game: `python -X utf8 tools/debug/show.py 2179_000 ... [--rom build/deltora_en.nds --lang en]` (text viewer, docs/re/debug.md)
- Unpack for recon: `python -X utf8 tools/unpack.py` -> work/fs/ (arm9, overlays, FILEDATA files)
- Release:  `python -X utf8 tools/release.py` (xdelta patch + verify; never publish without the user)
- Clean:    `python -X utf8 tools/clean.py` (published projects: lists rebuildable/downloadable files; `--yes` deletes)

## Paths
- Original ROM: `rom/1415 - Deltora Quest - 7-tsu no Houseki (J)(Caravan).nds` (gitignored; SHA-1 in `rom.sha1`, checked by `tools/check_rom.py`). Emulator: this repo's own DeSmuME QA fork in `tools/desmume/` (release `qa-2`, https://github.com/minhnhattonthat/desmume/releases/download/qa-2/desmume-qa-51b26329-win64.zip; gitignored; settings in `tools/emu-config/`). Savestates: `work/states/`.
- Text: `script/<file>.json` (FILEDATA 2178-2200; `tools/text.py dump [--refresh]`). Tables: `tbl/` (jp.tbl kanji were read from the font by eye). Glossary: `glossary.md`. RE notes index: `docs/re/README.md`. Fonts and their licences: `docs/fonts.md`.

## Rulings
- Edit source files (.py .lua .asm .tbl .json) only with the file-edit tool; scripts here read and analyse, never `.replace()` and write back.
- The user's decisions, with the options and reasons: `docs/decisions.md`. Read it before asking the user anything; add each new ruling there the same session.
- Subagents: dispatch the `.claude/agents/` types (translator, reviewer, visual-qa, playtester), never general-purpose: their short tool list cuts each agent's start-up context from ~43k to ~9k tokens.
- Player bug reports: GitHub issues (`gh issue list --label bug`). Copy the attached save into `work/states/`, reproduce in the emulator, fix, commit with `Fixes #N`, and update `docs/status.md`.
- Names come from the English Deltora Quest novels (Emily Rodda), not romanized katakana. See `glossary.md`.
- Intro movie: Start/A don't skip it; a touch (`t128,96`) does. Dialogue advances on touch, not A.
- Lua exec hooks need `--debugger` (JIT misses them). A Lua syntax error shows up as emu.py timeout (exit 124).

## Status
`docs/status.md`: done, next, open bugs. Update it at the end of every session.
