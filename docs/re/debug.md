# Debug tool

## Scenes (tools/debug/warp.py + scenes.json)
Cold boot + New Game route; `warp: [chapter, area]` makes New Game start in that stage (its own intro plays), and
`event: [script, n]` replaces the n-th LoadExecEvent with any event script (docs/re/events.md). Touch-mash advances
dialogue; A does not. States: `work/states/<scene>.dst`. `--all --jobs 4` regenerates every state.
Reached: title, entry card, prologue, chapters 1-8, tower, world map, smithy, paint screen, a cutscene layout,
field menu + sub-menus, ch1 boss fight (warp [1, 3]), game over (from the boss state, no input).
Not yet: staff roll (CallStaffRoll has no script caller), shop/compound menus (scripts found, need the menu
opened), a special move (banner), the battle HUD panel, a save point, chapter/area title cards.
Field play (verified 2026-10-18): one short tap walks Lief to that spot (holding or the D-pad only turns him);
touching an object (the red ring = sign) runs its event; slashes on an enemy hit it. Warp timing varies between
runs, so derive a scene from another scene's state (`from`) when the moment matters (game_over does this).
Dead ends: the world map warp (event 2609 swapped in for 2608) freezes on its first frame, taps and keys do
nothing; plain warp [0, 2] boots to black; event 1798 plays its recap then goes black (~f7000), so its SavePoint
is not reached; mashing at (128,96) in the boss fight does not land a special move (needs a hit at the
biorhythm peak; HP address not found: 0x021DEB76 and 0x02220D04 are not it).
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
