# Debug tool

## Scenes (tools/debug/warp.py + scenes.json)
Cold boot + New Game route; `warp: [chapter, area]` makes New Game start in that stage (its own intro plays), and
`event: [script, n]` replaces the n-th LoadExecEvent with any event script (docs/re/events.md). Touch-mash advances
dialogue; A does not. States: `work/states/<scene>.dst`. `--all --jobs 4` regenerates every state.
Reached: title, entry card, prologue, chapters 1-8, tower, world map, smithy, paint screen, a cutscene layout,
field menu + sub-menus, ch1 boss fight (warp [1, 3]), game over (from the boss state, no input), special move
banner "First Slash" (boss_ch1 + nodamage.lua + taps cycling over the boss, f685 and f2335: work/qa/god4),
camp (tent in ch1 area 1, SAVE panel). With nodamage the boss falls by ~f6500 and the story runs on (Jasmine).
Not yet: staff roll (CallStaffRoll has no script caller), shop/compound menus (scripts found, need the menu
opened), the battle HUD panel, chapter/area title cards (EpiTitle is only in the map script 2609; the area
cards were not shown by warps into areas, nor on entering the camp).
Field play (verified 2026-10-18): one short tap walks Lief to that spot (holding or the D-pad only turns him);
touching an object (the red ring = sign) runs its event; a tap on a nearby enemy attacks it, and an attack while
Filli is at the top of the biorhythm is a special move (banner on the top screen). Warp timing varies between
runs, so derive a scene from another scene's state (`from`) when the moment matters (game_over does this).
- `tools/debug/nodamage.lua` (verified in boss_ch1): pins player HP to max. HP = 20.12 fixed point at player
  object + 0xBC (max + 0xC0); hearts = (HP >> 12) / 10. The bytes at 0x0221FDA8 / AC are only the hearts
  display copy (pinning them keeps the hearts drawn but Lief still falls).
- Battle HUD panel (G16, sheet 5592): loaded by 0x02065554 (per-frame, from 0x02061D90) only while
  [obj + 0x1358] is set; probably a timed weapon bonus (smithing), so a plain fight never shows it.
Dead ends: the world map warp (event 2609 swapped in for 2608, or for 1811 after 2608 at stage [0, 3]) freezes
on its first frame, taps and keys do nothing; plain warp [0, 2] boots to black; event 1798 plays its recap then goes black (~f7000), so its SavePoint
is not reached.
The ch1 sign line '!eraweB !regnaD' is meant to be mirrored (2180_001, glossary).

## Text viewer (tools/debug/show.py + textview.lua) (verified: ids, rulers and 4-line text in real windows)
- 0x0204D234(r0 window, r1 file, r2 index) is the game's message loader (file = FILEDATA number, e.g. 2179).
  The viewer rewrites r1/r2 so the game loads the requested line itself (its own header, name tag, portrait).
- Raw text ("=..."): after the loader returns (0x0204C290 / 0x0204C410, window in r4) the viewer swaps
  `[w+0x20]` ptr, `[w+0x24]` length and `[w+0x54]` most lines per page (sizes the bitmap); text goes to 0x023C0000.
- Each injected window is shot 60 and 120 frames after it loads: OUT/text_<k>_<delay>.png.
- Needs `--debugger` (interpreter): under JIT exec hooks at function entries are missed (DeSmuME QA fork qa-2).
- 0x0204D6FC expands {var}s (runs only when the line has some); 0x0204DACC draws a page.
- 0x023C0000: zero in every RAM dump so far (title, entry card, opening). Re-check if the viewer misbehaves later.

## Other probes
- `tools/debug/drawlog.lua`: every renderer call (caller, window, string ptr, length, pitch). Needs `--debugger`.
- `tools/debug/dump_at.lua`: RAM + VRAM dump at DUMP_AT.
- `tools/findinram.py`: which archive files are resident in a RAM dump.
