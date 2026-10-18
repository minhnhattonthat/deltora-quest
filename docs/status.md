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
  2. Graphics text (docs/re/graphics.md): G1-G5 done (logo + (C) lines tools/logo.py; name tags + Yes/No
     tools/tags.py; Kuren/Rai/Niji/Dodge are Hepburn guesses, glossary `?`). Next: survey menus, shop, game over,
     staff roll, chapter-clear screens (need scenes in tools/debug/scenes.json first).
  3. Polish pass over docs/polish-todo.md (line by line, no bulk rewrites); whole-project sampled review.
  4. In-game checks noted by reviewers: hideout song puzzle (2188_136), smithing icons Circle/Arrow (2196_012),
     speakers 2184_248 / 2188_365 / 2199_116, 2197_216 context.
  5. Release tooling: xdelta patch, README with base hashes, jp_left scan, debug tool off.
- **Open questions:**
  - D7: game-renamed characters (ルーカス/スカール) use the novel names Steven/Nevets - waiting on the user.
  - Credits: company アウディオ English name, some staff-name readings unverified.
  - Glossary rows marked `?` (Elstedd, ...) from memory.
- **Waiting on the user:** D7.
