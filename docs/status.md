# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 6 done (whole script translated and reviewed), 8 started (visual QA of the English build).
  Last build: `build/deltora_en.nds` (2026-10-18), all 19 scenes in tools/debug/scenes.json boot and reach their
  screens (work/qa/tour_en). Lint: 3,655 lines, 0 errors.
- **Done:** repo + guardrails (fan-translation-template layout, 2026-10-25, D11); identity rebuild; extraction + kanji table; debug tool (stage/event warps, text
  viewer); VWF + English font; width gate + lint; glossary (novel names); translation of all 32 batches with a
  reviewer per batch (no Critical left; Important fixed); deferred Minor items in docs/polish-todo.md.
- **Next:**
  1. Visual QA gate: `qa_gate.py check work/qa/manifest.tsv work/qa/verdicts` must pass; fix issues it finds.
     Shots are every 300 frames: add denser routes per chapter (text viewer `tools/debug/show.py` per scene).
  2. Graphics text (docs/re/graphics.md G1-G18): whole-FILEDATA survey done (every BG screen and sprite cell,
     tools/debug/gfxsurvey.py + objsurvey.py; objsurvey skipped 193 banks until 2026-10-18, re-read by hand: 7
     more move banners (D10) + the minigame prompt G18 found and done) and every row handled: logo.py, tags.py,
     cards.py, menu.py (D8, engine re-pack), banners.py (D9, D10), sprites.py. Seen in game: logo, tags, Yes/No,
     field menu, item header, game over, "First Slash" banner, SAVE panel, "Tap Rapidly!" (scenes boss_ch1,
     game_over, camp, smithy; hook tools/debug/nodamage.lua). Imported but NOT seen in game: chapter/area cards (only the world map
     script shows them, and its warp freezes), battle HUD (needs a timed weapon bonus), Emily letter, card trade,
     demo screens (low risk: same import paths as items seen; sprite edits are pixel-only, no twins). Left: G14
     font sheet's user (probably debug menu), 354 working-title logo (no reference found). Dead ends and field
     controls: docs/re/debug.md. Next way to the cards: play ch1 to its end from boss_ch1 with nodamage + taps.
     Savestates go stale after every rebuild (cached file offsets): a stale dialogue.dst froze the emulator under
     --debugger. Run `warp.py --all` after each build before using states.
  3. Polish pass over docs/polish-todo.md (line by line, no bulk rewrites); whole-project sampled review.
  4. In-game checks noted by reviewers: seen in the text viewer 2026-10-18 and fine: 2188_136 (song line; the
     puzzle answer itself not played), 2184_248, 2188_365 (Barda), 2199_116 (Barda). Left: smithing icons
     Circle/Arrow (2196_012: the materials window after forging, smithy scene + taps), 2197_216 context.
  5. Release: `tools/release.py --version X.Y` (fresh build, smoke, jp_left on text files + arm9, qa_gate, xdelta
     re-apply check, README from docs/release-readme.txt, zip). v0.9 published 2026-10-19 as a GitHub release
     (repo is private, so the release is too). Debug tool is Lua/savestate only, nothing in the ROM.
     Update the README's known issues before each release.
- **Open questions:**
  - Credits: company アウディオ English name, some staff-name readings unverified.
  - Glossary rows marked `?` (Elstedd, ...) from memory.
- **Waiting on the user:** nothing (D7-D9 answered 2026-10-18).
