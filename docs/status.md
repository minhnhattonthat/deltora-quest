# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 5 (engine spike done; width gate next). Phases 1-4 done except: graphics-text survey (phase 1) and
  story/chapter warps (phase 2). Last build: `build/deltora_marker.nds` (2026-10-18), boots, smoke ok.
- **Done:** repo + guardrails; LF2 archive + byte-identical ROM rebuild; text found (FILEDATA 2178-2200, 3,665
  lines) with exact roundtrip; kanji table (684 used codes read from the font by eye + context review); route-based
  scene warps + state regen; in-game text viewer (`tools/debug/show.py`); VWF in ITCM + project-drawn English font;
  marker build (`tools/build.py --marker`).
- **Next:**
  1. Width gate: measure each window type with the marker build / text viewer (portrait dialogue, narration over
     pictures, top-screen prompts, title button, はじめから panel, name tags, menus, item lists) -> budgets in
     docs/re/windows.md + a px-width lint using fontgen advances.
  2. Graphics-text survey (docs/re/graphics.md): title logo subtitle 7つの宝石, (C) line, はい/いいえ labels,
     book cover, chapter cards, menus seen in the marker build that stayed Japanese.
  3. Story warps: map story-progress RAM / event dispatcher; add chapter, world map, shop, battle, ending entries.
  4. Glossary from the novels (characters, places, gems, monsters), then translation batches.
- **Open bugs:** text viewer leaves a garbage blob at bottom-right for a long injected line (2193_030), debug only.
- **Waiting on the user:** none.
