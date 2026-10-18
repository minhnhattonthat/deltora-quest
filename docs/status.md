# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 6 done (whole script translated and reviewed), 8 started (visual QA of the English build).
  Last build: `build/deltora_en.nds` (2026-10-18), all 19 scenes in tools/debug/scenes.json boot and reach their
  screens (work/qa/tour_en). Lint: 3,655 lines, 0 errors.
- **Done:** repo + guardrails; identity rebuild; extraction + kanji table; debug tool (stage/event warps, text
  viewer); VWF + English font; width gate + lint; glossary (novel names); translation of all 32 batches with a
  reviewer per batch (no Critical left; Important fixed); deferred Minor items in docs/polish-todo.md.
- **Next:**
  1. Visual QA gate: `qa_gate.py check work/qa/manifest.tsv work/qa/verdicts` must pass; fix issues it finds.
     Shots are every 300 frames: add denser routes per chapter (text viewer `tools/debug/show.py` per scene).
  2. Graphics text (docs/re/graphics.md G1-G17): whole-FILEDATA survey done (every BG screen and sprite cell,
     tools/debug/gfxsurvey.py + objsurvey.py, read by reviewer agents) and every row handled: logo.py, tags.py,
     cards.py, menu.py (D8, engine re-pack), banners.py (D9), sprites.py. Seen in game: logo, tags, Yes/No, field
     menu, item header. Imported but NOT seen in game yet (no scene reaches them): chapter/area cards, game over,
     move banners, battle HUD, Save panel, Emily letter, card trade, demo screens. Left: G14 font sheet's user
     (probably debug menu), 354 working-title logo (no reference found).
     Next: scenes for story select / world map (chapter cards), a battle with special moves, game over, save
     point, staff roll; then look at each imported item there. work/states/menu_card.dst hangs on load (made
     from ch1 + route): regenerate it, or go via `menu`.
  3. Polish pass over docs/polish-todo.md (line by line, no bulk rewrites); whole-project sampled review.
  4. In-game checks noted by reviewers: hideout song puzzle (2188_136), smithing icons Circle/Arrow (2196_012),
     speakers 2184_248 / 2188_365 / 2199_116, 2197_216 context.
  5. Release tooling: xdelta patch, README with base hashes, jp_left scan, debug tool off.
- **Open questions:**
  - Credits: company アウディオ English name, some staff-name readings unverified.
  - Glossary rows marked `?` (Elstedd, ...) from memory.
- **Waiting on the user:** nothing (D7-D9 answered 2026-10-18).
