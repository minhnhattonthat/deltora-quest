# Event engine and stages

## Scripts (verified: names found in arm9 and in SCR0 files; handlers logged with tools/debug/cmdlog.lua)
- Event scripts are `SCR0` files in FILEDATA (~460, ids 1794-2620). They import commands by name
  (StageSet2, LoadExecEvent, Message*, CallShop, ...).
- Command table in arm9 at 0x020B9xxx, 16-byte entries {name ptr, signature ptr, handler, flags}. Handlers take a
  call context in r0; `0x02028D34(ctx, i)` returns integer argument i, `0x02028DA4` a pointer argument.
  - StageSet2 0x0203E7A8 (chapter, area) -> `stage_set` 0x0203AF14(game, chapter, area)
  - LoadExecEvent 0x0203E0E4 -> 0x02039B78: args (script file, entry, 0, 0); ints read at 0x02039C1C/C2C/C3C/C4C
  - StageSet 0x0203E72C, ChangeStage 0x02042DC0, CallStaffRoll 0x02047878 (no script imports it: native caller)
- Game object 0x021D4A44: +0xC4 chapter, +0xC8 area, +0xB4 stage descriptor.

## Stages (verified: warps land in each chapter, work/qa/warp/chapters.png)
Descriptor table at arm9 0x020BAA70: 0xA10 bytes per chapter, 0x142 per area. Halfword 0 = message file for the
area; halfwords 8k+7 = event script of entrance k.

| chapter | areas | message file | what |
|---|---|---|---|
| 0 | 1 | 2199 | title / system |
| 0 | 2 | 2190 | farm / shop area (scripts 2600-2609) |
| 0 | 3-7 | 2179 | castle prologue (3 = library) |
| 1-8 | 1-7 | 2180-2188 | chapters 1-8 (2181 = chapter 1 second half) |
| 9 | 1-2 | 2178 | epilogue / cutscenes (1798-1803) |
| 9 | 3-6 | 2194 | むげんの塔 floors (script 2612) |

## New Game flow (warp hook point)
Title script 1797 -> StartGame -> `StageSet2(0, 3)` + `LoadExecEvent(2608, 99)`; 2608 picks the stage's intro event
(1811 for the castle, 1837 for chapter 1) and loads it. `tools/debug/warp.lua` swaps the stage (CH, AREA) and
optionally the n-th LoadExecEvent (EV, EVN). Event scripts that open menus: 2609 world map (+CallShop, CallCamp),
2606 CallCompound, 1814 / 2234 CallSmith, 1817 / 1821 CallPaint, 1798 / 2595 SavePoint.
