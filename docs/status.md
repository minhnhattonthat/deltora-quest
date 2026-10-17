# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 6 (translation). Pilot (mine + 3 agent batches b000-b002, 417 lines) reviewed, fixed, merged.
  Wave 2 (b003-b008) dispatched 2026-10-18; batches b003-b031 split in work/batches (regenerate with
  `tools/batches.py split` if work/ was lost: only untranslated lines are split).
- **Done:** repo + guardrails; identity rebuild; text extraction + kanji table; debug tool (route scenes, stage and
  event warps: chapters 1-8, tower, world map, smithy, cutscene; text viewer); VWF + English font; width gate
  (portrait box 2 lines x 240 px; narration centred 240 px); lint; graphics survey (docs/re/graphics.md);
  glossary (novel names), synopsis, briefs, style reference.
- **Next:**
  1. Translation waves b009-b031: dispatch "Read docs/translator-brief.md and follow it for batch bNNN", then
     `tools/batches.py merge bNNN`, reviewer per batch (docs/reviewer-brief.md, sonnet), fix Critical/Important,
     defer Minor to docs/polish-todo.md. Merge NEW TERMs into glossary.md between waves.
  2. Graphics (phase 7/8): logo FILEDATA 465 (G1/G2), copyright line (G3), はい/いいえ (G4: check), speaker name
     tags (G5). Find menus/shop/game over/staff roll scenes and survey them.
  3. QA tours on the English build per chapter (warp scenes), visual-QA gate, then release tooling (xdelta).
- **Open bugs / questions:**
  - D7: game-renamed characters (ルーカス/スカール = Steven/Nevets?) provisionally given novel names: ask the user.
  - Credits: company アウディオ English name and several staff-name readings unverified (docs/polish-todo.md).
  - Unverified novel spellings in glossary rows marked `?` (Elstedd, ...).
- **Waiting on the user:** D7.
