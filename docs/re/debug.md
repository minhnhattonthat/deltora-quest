# Debug tool

## Scenes (tools/debug/warp.py + scenes.json)
Route-based from cold boot (touch-mash advances dialogue; A does not). States: `work/states/<scene>.dst`.
Story chapters, world map, shops, battles, endings and credits are **not reachable yet**: next step is mapping the
story-progress variables (RAM search across save points) or the event dispatcher, then adding flag-based entries.

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
