# Debug tool

## Scenes (tools/debug/warp.py + scenes.json)
Route-based from cold boot (touch-mash advances dialogue; A does not). States: `work/states/<scene>.dst`.
Story chapters, world map, shops, battles, endings and credits are **not reachable yet**: next step is mapping the
story-progress variables (RAM search across save points) or the event dispatcher, then adding flag-based entries.

## Text viewer (tools/debug/show.py + textview.lua) (verified: 3 lines shown in real windows, work/qa/show)
- Hook at the string renderer entry (arm9 0x0204DACC, r0 = window). The first time a window draws a string, its
  `[w+0x20]` pointer and `[w+0x24]` length are swapped for the next requested line, written to RAM at 0x023C0000.
- The window's name tag and portrait still come from the original line's header.
- Needs `--debugger` (interpreter): under JIT the exec hook at 0x0204DACC is missed (DeSmuME QA fork qa-2).
- 0x023C0000: zero in every RAM dump so far (title, entry card, opening). Re-check if the viewer misbehaves later.

## Other probes
- `tools/debug/drawlog.lua`: every renderer call (caller, window, string ptr, length, pitch). Needs `--debugger`.
- `tools/debug/dump_at.lua`: RAM + VRAM dump at DUMP_AT.
- `tools/findinram.py`: which archive files are resident in a RAM dump.
